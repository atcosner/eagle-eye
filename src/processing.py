import cv2
import logging
import numpy as np
from google.cloud import vision
from pathlib import Path

from src.definitions.util import BoxBounds
from .definitions.fields import TextField, TextFieldOrCheckbox, MultiCheckboxField, CheckboxField, FormField

from .util import sanitize_filename
from .definitions.results import TextResult, CheckboxMultiResult, CheckboxResult, FieldResult, TextOrCheckboxResult

OCR_WHITE_PIXEL_THRESHOLD = 0.99  # Ignore images that are over X% white
CHECKBOX_WHITE_PIXEL_THRESHOLD = 0.5  # Checked checkboxes should have less than X% white

logger = logging.getLogger(__name__)
client = vision.ImageAnnotatorClient()


def snip_roi_image(image: np.array, bounds: BoxBounds, save_path: Path | None = None) -> np.array:
    roi = image[bounds.y:bounds.y + bounds.height, bounds.x:bounds.x + bounds.width]
    if save_path is not None:
        assert not save_path.exists(), f'Path ({save_path}) already exists!'
        cv2.imwrite(str(save_path), roi)

    return roi


def ocr_text_region(image: np.array, region: BoxBounds) -> str:
    roi = image[region.y:region.y + region.height, region.x:region.x + region.width]
    _, buffer = cv2.imencode('.jpg', roi)

    # TODO: Should we use the REST API here?
    # TODO: Add an english language hint
    image = vision.Image(content=buffer.tobytes())
    response = client.text_detection(image=image)

    # There are likely any results so choose the longest one
    ocr_string = ''
    for text in response.text_annotations:
        if len(text.description) > len(ocr_string):
            ocr_string = text.description

    # Clean up the string
    ocr_string = ocr_string.strip().replace('\n', ' ')
    logger.info(f'Detected: "{ocr_string}"')
    return ocr_string


def process_text_field(working_dir: Path, aligned_image: np.array, page_region: str, field: TextField) -> TextResult:
    # Extract the region of interest from the larger image
    roi = snip_roi_image(aligned_image, field.region)
    total_pixels = field.region.height * field.region.width

    # Apply pre-processing to the ROI
    updated_roi = cv2.copyMakeBorder(roi, 10, 10, 10, 10, cv2.BORDER_CONSTANT, None, (255, 255, 255))

    # Save the image off for further analysis
    roi_image_path = working_dir / f'{sanitize_filename(field.name)}.png'
    assert not roi_image_path.exists(), f'Path ({roi_image_path}) already exists!'
    cv2.imwrite(str(roi_image_path), updated_roi)

    # Threshold the image to determine if there is text in it
    inner_roi = aligned_image[
        field.region.y + (field.region.height // 10):field.region.y + field.region.height - (field.region.height // 10),
        field.region.x:field.region.x + field.region.width
    ]
    _, threshold = cv2.threshold(inner_roi, 127, 255, cv2.THRESH_BINARY)
    white_pixels = cv2.countNonZero(threshold)
    logger.debug(f'White: {white_pixels}, Total: {total_pixels}, Pct: {white_pixels / total_pixels}')

    if (white_pixels / total_pixels) <= OCR_WHITE_PIXEL_THRESHOLD:
        ocr_result = ocr_text_region(aligned_image, field.region)

        # TODO: Result verification and correction here
    else:
        logger.info(f'Detected white image (>= {OCR_WHITE_PIXEL_THRESHOLD:.2%}), skipping OCR')
        ocr_result = ''

    return TextResult(
        field_name=field.name,
        page_region=page_region,
        roi_image_path=roi_image_path,
        field=field,
        text=ocr_result,
    )


def get_checked(aligned_image: np.array, region: BoxBounds) -> bool:
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
        aligned_image: np.array,
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
        aligned_image: np.array,
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
        checked=get_checked(aligned_image, field.region),
    )


def process_text_or_checkbox(
        working_dir: Path,
        aligned_image: np.array,
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
        text = ocr_text_region(aligned_image, field.text_region)

    return TextOrCheckboxResult(
        field_name=field.name,
        page_region=page_region,
        roi_image_path=visual_region_image_path,
        field=field,
        text=text,
    )


def process_fields(working_dir: Path, aligned_image_path: Path, page_region: str, fields: list[FormField]) -> list[FieldResult]:
    # Load the aligned image
    aligned_image = cv2.imread(str(aligned_image_path), flags=cv2.IMREAD_GRAYSCALE)

    # Process each field depending on its type
    results = []
    for field in fields:
        logger.info(f'Processing field: {field.name}')

        if isinstance(field, TextField):
            result = process_text_field(working_dir=working_dir, aligned_image=aligned_image, page_region=page_region, field=field)
        elif isinstance(field, MultiCheckboxField):
            result = process_checkbox_multi_field(working_dir=working_dir, aligned_image=aligned_image, page_region=page_region, field=field)
        elif isinstance(field, CheckboxField):
            result = process_checkbox_field(working_dir=working_dir, aligned_image=aligned_image, page_region=page_region, field=field)
        elif isinstance(field, TextFieldOrCheckbox):
            result = process_text_or_checkbox(working_dir=working_dir, aligned_image=aligned_image, page_region=page_region, field=field)
        else:
            logger.warning(f'Unknown field type: {type(field)}')
            continue

        results.append(result)

    return results
