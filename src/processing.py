import base64
import cv2
import logging
import numpy as np
import requests
from google.cloud import vision
from pathlib import Path

import src.definitions.base_fields as base_fields
import src.definitions.processed_fields as processed_fields
import src.validation.util as validation_util
from src.definitions.util import BoxBounds

from .util import sanitize_filename

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


def should_copy_from_previous(prev_text: str) -> bool:
    # TODO: Be smarter about this
    copy_values = ['11', '=', '"']
    return any([value in prev_text for value in copy_values])


def process_text_field(
        session: requests.Session,
        roi_dest_path: Path,
        aligned_image: np.ndarray,
        page_region: str,
        field: base_fields.TextField,
        prev_field: processed_fields.TextProcessedField | None,
) -> processed_fields.TextProcessedField:
    snip_roi_image(aligned_image, field.visual_region, save_path=roi_dest_path)

    if should_ocr_region(aligned_image, field.visual_region):
        ocr_result = ocr_text_region(session, aligned_image, field.visual_region, add_border=True)
    else:
        logger.info(f'Detected white image (>= {OCR_WHITE_PIXEL_THRESHOLD:.2%}), skipping OCR')
        ocr_result = ''

    # Check if this field could be copied from above
    allow_linking = prev_field is not None and field.allow_copy
    copied_from_previous = False
    if allow_linking and should_copy_from_previous(ocr_result):
        copied_from_previous = True
        ocr_result = prev_field.text

    return processed_fields.TextProcessedField(
        name=field.name,
        page_region=page_region,
        roi_image_path=roi_dest_path,
        validation_result=field.validator.validate(ocr_result),
        base_field=field,
        text=ocr_result,
        allow_linking=allow_linking,
        copied_from_previous=copied_from_previous,
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


def process_multi_checkbox_field(
        session: requests.Session,
        roi_dest_path: Path,
        aligned_image: np.ndarray,
        page_region: str,
        field: base_fields.MultiCheckboxField,
) -> processed_fields.MultiCheckboxProcessedField:
    snip_roi_image(aligned_image, field.visual_region, save_path=roi_dest_path)

    # Check each option in the field
    checkboxes: dict[str, processed_fields.MultiCheckboxProcessedOption] = {}
    for checkbox in field.checkboxes:
        checked = get_checked(aligned_image, checkbox.region)
        optional_text: str | None = None

        if checkbox.text_region is not None:
            if should_ocr_region(aligned_image, checkbox.text_region):
                optional_text = ocr_text_region(session, aligned_image, checkbox.text_region, add_border=True)
            else:
                optional_text = ''

        checkboxes[checkbox.name] = processed_fields.MultiCheckboxProcessedOption(
            name=checkbox.name,
            checked=checked,
            text=optional_text,
        )

    validation_format = [(checkbox.checked, checkbox.text) for checkbox in checkboxes.values()]

    return processed_fields.MultiCheckboxProcessedField(
        name=field.name,
        page_region=page_region,
        roi_image_path=roi_dest_path,
        validation_result=field.validator.validate(validation_format),
        base_field=field,
        checkboxes=checkboxes,
    )


def process_checkbox_field(
        roi_dest_path: Path,
        aligned_image: np.ndarray,
        page_region: str,
        field: base_fields.CheckboxField,
) -> processed_fields.CheckboxProcessedField:
    snip_roi_image(aligned_image, field.visual_region, save_path=roi_dest_path)

    checked = get_checked(aligned_image, field.checkbox_region)
    return processed_fields.CheckboxProcessedField(
        name=field.name,
        page_region=page_region,
        roi_image_path=roi_dest_path,
        validation_result=field.validator.validate(checked),
        base_field=field,
        checked=checked,
    )


def process_text_or_checkbox_field(
        session: requests.Session,
        roi_dest_path: Path,
        aligned_image: np.ndarray,
        page_region: str,
        field: base_fields.TextOrCheckboxField,
) -> processed_fields.TextOrCheckboxProcessedField:
    snip_roi_image(aligned_image, field.visual_region, save_path=roi_dest_path)

    checked = get_checked(aligned_image, field.checkbox_region)
    has_text = should_ocr_region(aligned_image, field.text_region)
    if checked:
        text = field.checkbox_text
    elif has_text:
        text = ocr_text_region(session, aligned_image, field.text_region)
    else:
        logger.warning('Text or Checkbox was not checked but also did not have text?')
        text = ''

    # Handle an empty field
    if not checked and not has_text:
        validation_result = validation_util.ValidationResult(
            state=validation_util.ValidationState.MALFORMED,
            reasoning='Checkbox or text required',
        )
    else:
        validation_result = field.validator.validate(text)

    return processed_fields.TextOrCheckboxProcessedField(
        name=field.name,
        page_region=page_region,
        roi_image_path=roi_dest_path,
        validation_result=validation_result,
        base_field=field,
        text=text,
    )


def process_multiline_text_field(
        session: requests.Session,
        roi_dest_path: Path,
        aligned_image: np.ndarray,
        page_region: str,
        field: base_fields.MultilineTextField,
) -> processed_fields.MultilineTextProcessedField:
    snip_roi_image(aligned_image, field.visual_region, save_path=roi_dest_path)

    # Multiline images need to be stitched together for OCR
    stitched_image = stitch_images(aligned_image, field.line_regions)

    # Check if any of our regions need to be OCR'd
    ocr_checks = [should_ocr_region(aligned_image, region) for region in field.line_regions]

    if any(ocr_checks):
        ocr_result = ocr_text_region(session, roi=stitched_image, add_border=True)
    else:
        logger.info(f'Detected white image (>= {OCR_WHITE_PIXEL_THRESHOLD:.2%}), skipping OCR')
        ocr_result = ''

    return processed_fields.MultilineTextProcessedField(
        name=field.name,
        page_region=page_region,
        roi_image_path=roi_dest_path,
        validation_result=field.validator.validate(ocr_result),
        base_field=field,
        text=ocr_result,
    )


def process_fields(
        session: requests.Session,
        working_dir: Path,
        aligned_image_path: Path,
        page_region: str,
        region_fields: list[base_fields.BaseField],
        prev_region_fields: list[processed_fields.BaseProcessedField] | None,
) -> list[processed_fields.BaseProcessedField]:
    # Load the aligned image
    aligned_image = cv2.imread(str(aligned_image_path), flags=cv2.IMREAD_GRAYSCALE)

    # Process each field depending on its type
    results = []
    for base_field in region_fields:
        logger.info(f'Processing field: {base_field.name}')
        roi_dest_path = working_dir / f'{sanitize_filename(base_field.name)}.png'

        # Find the instance of this field in the previous region
        prev_region_field = None
        if prev_region_fields is not None:
            for field in prev_region_fields:
                if field.name == base_field.name:
                    prev_region_field = field

        if isinstance(base_field, base_fields.TextField):
            result = process_text_field(
                session=session,
                roi_dest_path=roi_dest_path,
                aligned_image=aligned_image,
                page_region=page_region,
                field=base_field,
                prev_field=prev_region_field,
            )
        elif isinstance(base_field, base_fields.MultiCheckboxField):
            result = process_multi_checkbox_field(
                session=session,
                roi_dest_path=roi_dest_path,
                aligned_image=aligned_image,
                page_region=page_region,
                field=base_field,
            )
        elif isinstance(base_field, base_fields.CheckboxField):
            result = process_checkbox_field(
                roi_dest_path=roi_dest_path,
                aligned_image=aligned_image,
                page_region=page_region,
                field=base_field,
            )
        elif isinstance(base_field, base_fields.TextOrCheckboxField):
            result = process_text_or_checkbox_field(
                session=session,
                roi_dest_path=roi_dest_path,
                aligned_image=aligned_image,
                page_region=page_region,
                field=base_field,
            )
        elif isinstance(base_field, base_fields.MultilineTextField):
            result = process_multiline_text_field(
                session=session,
                roi_dest_path=roi_dest_path,
                aligned_image=aligned_image,
                page_region=page_region,
                field=base_field,
            )
        else:
            logger.warning(f'Unknown field type: {type(base_field)}')
            continue

        results.append(result)

    return results
