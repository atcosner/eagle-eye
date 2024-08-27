import cv2
import logging
import pytesseract
from dataclasses import dataclass
from pathlib import Path

from src.definitions.util import OcrField

# Ignore images that are over X% white
OCR_WHITE_PIXEL_THRESHOLD = 0.99

logger = logging.getLogger(__name__)


@dataclass
class OcrResult:
    field: OcrField
    roi_image_path: Path
    extracted_text: str
    user_corrected_text: str | None = None


def process_ocr_field(working_dir: Path, aligned_image, field: OcrField) -> OcrResult:
    # Extract the region of interest from the larger image
    roi = aligned_image[
        field.region.y:field.region.y + field.region.height,
        field.region.x:field.region.x + field.region.width
    ]
    total_pixels = field.region.height * field.region.width

    # Apply pre-processing to the ROI
    updated_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2RGB)
    # updated_roi = cv2.GaussianBlur(updated_roi, (3, 3), 0)
    updated_roi = cv2.copyMakeBorder(updated_roi, 10, 10, 10, 10, cv2.BORDER_CONSTANT, None, (255, 255, 255))

    # Save the image off for further analysis
    sanitized_field_name = field.name.lower().replace(' ', '_')
    roi_image_path = working_dir / f'{sanitized_field_name}.png'
    assert not roi_image_path.exists(), f'Path ({roi_image_path}) already exists!'
    cv2.imwrite(str(roi_image_path), updated_roi)

    # Threshold the image to determine if there is text in it
    # TODO: Use the inner part of the image to remove top and bottom lines that appear after alignment
    _, threshold = cv2.threshold(roi, 127, 255, cv2.THRESH_BINARY)
    white_pixels = cv2.countNonZero(threshold)
    logger.info(f'White: {white_pixels}, Total: {total_pixels}, Pct: {white_pixels / total_pixels}')
    if (white_pixels / total_pixels) > OCR_WHITE_PIXEL_THRESHOLD:
        logger.info(f'Detected white image (>= {OCR_WHITE_PIXEL_THRESHOLD:.2%}), skipping OCR')
        return OcrResult(field=field, roi_image_path=roi_image_path, extracted_text='')

    # Attempt OCR on the image
    ocr_string = pytesseract.image_to_string(updated_roi, lang='eng', config=f'--psm {field.segment}')

    # Post-processing on the returned string

    return OcrResult(
        field=field,
        roi_image_path=roi_image_path,
        extracted_text=ocr_string.strip(),
    )


def process_ocr_regions(working_dir: Path, aligned_image_path: Path, fields: list[OcrField]) -> list[OcrResult]:
    # Load the aligned image
    aligned_image = cv2.imread(str(aligned_image_path), flags=cv2.IMREAD_GRAYSCALE)

    # Process each OCR field
    results = []
    for field in fields:
        logger.info(f'Processing OCR field: {field.name}')
        result = process_ocr_field(
            working_dir=working_dir,
            aligned_image=aligned_image,
            field=field,
        )
        results.append(result)

    return results
