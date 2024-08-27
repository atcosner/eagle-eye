import cv2
import logging

import numpy as np
import pytesseract
from pathlib import Path

from src.definitions.util import BoxBounds, FormField, TextField, CheckboxMultiField

from .util import sanitize_filename, OcrResult, CheckboxResult, FieldResult

OCR_WHITE_PIXEL_THRESHOLD = 0.99  # Ignore images that are over X% white

logger = logging.getLogger(__name__)


def snip_roi_image(image: np.array, bounds: BoxBounds) -> np.array:
    return image[bounds.y:bounds.y + bounds.height, bounds.x:bounds.x + bounds.width]


def process_text_field(working_dir: Path, aligned_image: np.array, field: TextField) -> OcrResult:
    # Extract the region of interest from the larger image
    roi = snip_roi_image(aligned_image, field.region)
    total_pixels = field.region.height * field.region.width

    # Apply pre-processing to the ROI
    # updated_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    # updated_roi = cv2.GaussianBlur(updated_roi, (3, 3), 0)
    updated_roi = cv2.copyMakeBorder(roi, 10, 10, 10, 10, cv2.BORDER_CONSTANT, None, (255, 255, 255))

    # Save the image off for further analysis
    roi_image_path = working_dir / f'{sanitize_filename(field.name)}.png'
    assert not roi_image_path.exists(), f'Path ({roi_image_path}) already exists!'
    cv2.imwrite(str(roi_image_path), updated_roi)

    # Threshold the image to determine if there is text in it
    # TODO: Use the inner part of the image to remove top and bottom lines that appear after alignment
    _, threshold = cv2.threshold(roi, 127, 255, cv2.THRESH_BINARY)
    white_pixels = cv2.countNonZero(threshold)
    logger.debug(f'White: {white_pixels}, Total: {total_pixels}, Pct: {white_pixels / total_pixels}')
    if (white_pixels / total_pixels) > OCR_WHITE_PIXEL_THRESHOLD:
        logger.info(f'Detected white image (>= {OCR_WHITE_PIXEL_THRESHOLD:.2%}), skipping OCR')
        return OcrResult(field_name=field.name, roi_image_path=roi_image_path, extracted_text='')

    # Attempt OCR on the image
    ocr_string = pytesseract.image_to_string(updated_roi, lang='eng', config=f'--psm {field.segment_option}')

    # Post-processing on the returned string

    return OcrResult(field_name=field.name, roi_image_path=roi_image_path, extracted_text=ocr_string.strip())


def process_checkbox_field(working_dir: Path, aligned_image: np.array, field: CheckboxMultiField) -> CheckboxResult:
    # Snip the visual region for debugging
    visual_region = snip_roi_image(aligned_image, field.visual_region)

    visual_region_image_path = working_dir / f'{sanitize_filename(field.name)}.png'
    assert not visual_region_image_path.exists(), f'Path ({visual_region_image_path}) already exists!'
    cv2.imwrite(str(visual_region_image_path), visual_region)

    # Check each option in the field
    selected_option: str | None = None
    for option in field.options:
        logger.info(f'Checking: {option.name}')

        option_roi = snip_roi_image(aligned_image, option.region)
        roi_pixels = option.region.height * option.region.width

        # Threshold and count the number of white pixels
        _, threshold = cv2.threshold(option_roi, 200, 255, cv2.THRESH_BINARY)
        white_pixels = cv2.countNonZero(threshold)
        logger.debug(f'White: {white_pixels}, Total: {roi_pixels}, Pct: {white_pixels / roi_pixels}')

        # Check if there are enough black pixels to confirm a selection
        if white_pixels != roi_pixels:
            selected_option = option.name

            # TODO: Do OCR if the selected option has a text region
            break

    return CheckboxResult(
        field_name=field.name,
        roi_image_path=visual_region_image_path,
        selected_option=selected_option,
    )


def process_fields(working_dir: Path, aligned_image_path: Path, fields: list[FormField]) -> list[FieldResult]:
    # Load the aligned image
    aligned_image = cv2.imread(str(aligned_image_path), flags=cv2.IMREAD_GRAYSCALE)

    # Process each field depending on its type
    results = []
    for field in fields:
        logger.info(f'Processing field: {field.name}')

        if isinstance(field, TextField):
            result = process_text_field(working_dir=working_dir, aligned_image=aligned_image, field=field)
            results.append(result)
        elif isinstance(field, CheckboxMultiField):
            result = process_checkbox_field(working_dir=working_dir, aligned_image=aligned_image, field=field)
            results.append(result)
        else:
            logger.warning(f'Unknown field type: {type(field)}')

    return results
