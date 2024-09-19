import base64
import cv2
import logging

import imutils
import numpy as np
import requests
from google.cloud import vision
from pathlib import Path

from src.definitions.util import BoxBounds
from .definitions.fields import TextField, TextFieldOrCheckbox, MultiCheckboxField, CheckboxField, MultilineTextField, FormField

from .util import sanitize_filename
from .definitions.results import TextResult, CheckboxMultiResult, CheckboxResult, FieldResult, TextOrCheckboxResult, MultilineTextResult

OCR_WHITE_PIXEL_THRESHOLD = 0.99  # Ignore images that are over X% white
CHECKBOX_WHITE_PIXEL_THRESHOLD = 0.5  # Checked checkboxes should have less than X% white

logger = logging.getLogger(__name__)
client = vision.ImageAnnotatorClient()


def snip_roi_image(image: np.ndarray, bounds: BoxBounds, save_path: Path | None = None) -> np.ndarray:
    roi = image[bounds.y:bounds.y + bounds.height, bounds.x:bounds.x + bounds.width]
    if save_path is not None:
        assert not save_path.exists(), f'Path ({save_path}) already exists!'
        cv2.imwrite(str(save_path), roi)

    return roi


def should_ocr_region(image: np.ndarray, region: BoxBounds, shrink_factor: float = 0.1) -> bool:
    total_pixels = region.height * region.width
    inner_roi = image[
        region.y + int(region.height * shrink_factor):region.y + region.height - int(region.height * shrink_factor),
        region.x:region.x + region.width
    ]

    # Threshold the image to determine if there is text in it
    _, threshold = cv2.threshold(inner_roi, 127, 255, cv2.THRESH_BINARY)
    white_pixels = cv2.countNonZero(threshold)
    logger.debug(f'White: {white_pixels}, Total: {total_pixels}, Pct: {white_pixels / total_pixels}')

    return (white_pixels / total_pixels) <= OCR_WHITE_PIXEL_THRESHOLD


def stitch_images(image: np.ndarray, regions: list[BoxBounds]) -> np.ndarray:
    total_width = sum([region.width for region in regions])
    max_height = max([region.height for region in regions])

    # Create a white canvas
    stitch_canvas = np.full(
        shape=(max_height, total_width),
        fill_value=255,
        dtype=np.uint8,
    )

    # Copy each image into the canvas
    cursor_x = 0
    for region in regions:
        roi = snip_roi_image(image, region)
        stitch_canvas[0:region.height, cursor_x:cursor_x + region.width] = roi

        cursor_x = cursor_x + region.width

    return stitch_canvas


def ocr_text_region(
        session: requests.Session,
        image: np.ndarray | None = None,
        region: BoxBounds | None = None,
        roi: np.ndarray | None = None,
        add_border: bool = False,
) -> str:
    if roi is None:
        assert image is not None
        assert region is not None
        roi = image[region.y:region.y + region.height, region.x:region.x + region.width]

    if add_border:
        roi = cv2.copyMakeBorder(roi, 10, 10, 10, 10, cv2.BORDER_CONSTANT, None, (255, 255, 255))

    _, buffer = cv2.imencode('.jpg', roi)
    encoded_bytes = base64.b64encode(buffer.tobytes()).decode('ascii')

    # https://cloud.google.com/vision/docs/ocr
    data_payload = {
        'requests': [
            {
                'image': {
                    'content': encoded_bytes,
                },
                'features': [
                    {
                        'type': 'TEXT_DETECTION',
                    }
                ],
                'imageContext': {
                    'languageHints': [
                        'en-t-i0-handwrit',
                    ],
                },
            },
        ],
    }

    result = session.post(
        'https://vision.googleapis.com/v1/images:annotate',
        json=data_payload,
    )
    result.raise_for_status()
    logger.debug(result.json())

    ocr_string: str | None = None
    for response in result.json()['responses']:
        if 'fullTextAnnotation' in response:
            ocr_string = response['fullTextAnnotation']['text']

    # Clean up the string
    if ocr_string is not None:
        ocr_string = ocr_string.strip().replace('\n', ' ')

    logger.info(f'Detected: "{ocr_string}"')
    return ocr_string if ocr_string is not None else ''


def process_text_field(
        session: requests.Session,
        working_dir: Path,
        aligned_image: np.ndarray,
        page_region: str,
        field: TextField,
) -> TextResult:
    roi_image_path = working_dir / f'{sanitize_filename(field.name)}.png'
    snip_roi_image(aligned_image, field.visual_region, save_path=roi_image_path)

    if should_ocr_region(aligned_image, field.visual_region):
        ocr_result = ocr_text_region(session, aligned_image, field.visual_region, add_border=True)
    else:
        logger.info(f'Detected white image (>= {OCR_WHITE_PIXEL_THRESHOLD:.2%}), skipping OCR')
        ocr_result = ''

    result, new_text = field.validator.validate(ocr_result, allow_correction=True)
    logger.info(f'Validation: result={result.name}, new_text="{new_text}"')

    return TextResult(
        field_name=field.name,
        page_region=page_region,
        roi_image_path=roi_image_path,
        field=field,
        validation_result=result,
        text=new_text,
    )


def get_checked(aligned_image: np.ndarray, region: BoxBounds) -> bool:
    option_roi = snip_roi_image(aligned_image, region)
    roi_pixels = region.height * region.width

    # Threshold and count the number of white pixels
    _, threshold = cv2.threshold(option_roi, 200, 255, cv2.THRESH_BINARY)
    white_pixels = cv2.countNonZero(threshold)
    logger.debug(f'White: {white_pixels}, Total: {roi_pixels}, Pct: {white_pixels / roi_pixels}')

    # Check if there are enough black pixels to confirm a selection
    return (white_pixels / roi_pixels) < CHECKBOX_WHITE_PIXEL_THRESHOLD


def process_checkbox_multi_field(
        working_dir: Path,
        aligned_image: np.ndarray,
        page_region: str,
        field: MultiCheckboxField,
) -> CheckboxMultiResult:
    # Snip the visual region for debugging
    visual_region_image_path = working_dir / f'{sanitize_filename(field.name)}.png'
    snip_roi_image(aligned_image, field.visual_region, save_path=visual_region_image_path)

    # Check each option in the field
    selected_options: list[str] = []
    for option in field.options:
        if get_checked(aligned_image, option.region):
            # TODO: Do OCR if the selected option has a text region
            selected_options.append(option.name)

    return CheckboxMultiResult(
        field_name=field.name,
        page_region=page_region,
        roi_image_path=visual_region_image_path,
        field=field,
        selected_options=selected_options,
    )


def process_checkbox_field(
        working_dir: Path,
        aligned_image: np.ndarray,
        page_region: str,
        field: CheckboxField,
) -> CheckboxResult:
    # Snip the visual region for debugging
    visual_region_image_path = working_dir / f'{sanitize_filename(field.name)}.png'
    snip_roi_image(aligned_image, field.visual_region, save_path=visual_region_image_path)

    return CheckboxResult(
        field_name=field.name,
        page_region=page_region,
        roi_image_path=visual_region_image_path,
        field=field,
        checked=get_checked(aligned_image, field.checkbox_region),
    )


def process_text_or_checkbox(
        session: requests.Session,
        working_dir: Path,
        aligned_image: np.ndarray,
        page_region: str,
        field: TextFieldOrCheckbox,
) -> TextOrCheckboxResult:
    # Snip the visual region for debugging
    visual_region_image_path = working_dir / f'{sanitize_filename(field.name)}.png'
    snip_roi_image(aligned_image, field.visual_region, save_path=visual_region_image_path)

    # See if the checkbox is checked first
    checked = get_checked(aligned_image, field.checkbox_region)
    if checked:
        text = field.checkbox_text
    else:
        text = ocr_text_region(session, aligned_image, field.text_region)

    return TextOrCheckboxResult(
        field_name=field.name,
        page_region=page_region,
        roi_image_path=visual_region_image_path,
        field=field,
        text=text,
    )


def process_multiline_text_field(
        session: requests.Session,
        working_dir: Path,
        aligned_image: np.ndarray,
        page_region: str,
        field: MultilineTextField,
) -> MultilineTextResult:
    roi_image_path = working_dir / f'{sanitize_filename(field.name)}.png'
    snip_roi_image(aligned_image, field.visual_region, save_path=roi_image_path)

    # Multiline images need to be stitched together for OCR
    stitched_image = stitch_images(aligned_image, field.line_regions)

    # Check if any of our regions need to be OCR'd
    ocr_checks = [should_ocr_region(aligned_image, region) for region in field.line_regions]

    if any(ocr_checks):
        ocr_result = ocr_text_region(session, roi=stitched_image, add_border=True)

        # TODO: Result verification and correction here
    else:
        logger.info(f'Detected white image (>= {OCR_WHITE_PIXEL_THRESHOLD:.2%}), skipping OCR')
        ocr_result = ''

    return MultilineTextResult(
        field_name=field.name,
        page_region=page_region,
        roi_image_path=roi_image_path,
        field=field,
        text=ocr_result,
    )


def process_fields(
        session: requests.Session,
        working_dir: Path,
        aligned_image_path: Path,
        page_region: str,
        fields: list[FormField],
) -> list[FieldResult]:
    # Load the aligned image
    aligned_image = cv2.imread(str(aligned_image_path), flags=cv2.IMREAD_GRAYSCALE)

    # Process each field depending on its type
    results = []
    for field in fields:
        logger.info(f'Processing field: {field.name}')

        if isinstance(field, TextField):
            result = process_text_field(session=session, working_dir=working_dir, aligned_image=aligned_image, page_region=page_region, field=field)
        elif isinstance(field, MultiCheckboxField):
            result = process_checkbox_multi_field(working_dir=working_dir, aligned_image=aligned_image, page_region=page_region, field=field)
        elif isinstance(field, CheckboxField):
            result = process_checkbox_field(working_dir=working_dir, aligned_image=aligned_image, page_region=page_region, field=field)
        elif isinstance(field, TextFieldOrCheckbox):
            result = process_text_or_checkbox(session=session, working_dir=working_dir, aligned_image=aligned_image, page_region=page_region, field=field)
        elif isinstance(field, MultilineTextField):
            result = process_multiline_text_field(session=session, working_dir=working_dir, aligned_image=aligned_image, page_region=page_region, field=field)
        else:
            logger.warning(f'Unknown field type: {type(field)}')
            continue

        results.append(result)

    return results
