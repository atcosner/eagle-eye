import cv2
import logging
import numpy as np
import re
from pathlib import Path

from src.database.fields.text_field import TextField
from src.database.processed_fields.processed_text_field import ProcessedTextField
from src.util.types import FormLinkingMethod

from .types import BoxBounds
from src.database.processing.processed_region import ProcessedRegion

OCR_WHITE_PIXEL_THRESHOLD = 0.99  # Ignore images that are over X% white
CHECKBOX_WHITE_PIXEL_THRESHOLD = 0.6  # Checked checkboxes should have less than X% white

logger = logging.getLogger(__name__)


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


def get_checked(aligned_image: np.ndarray, region: BoxBounds) -> bool:
    option_roi = snip_roi_image(aligned_image, region)
    roi_pixels = region.height * region.width

    # Threshold and count the number of white pixels
    _, threshold = cv2.threshold(option_roi, 200, 255, cv2.THRESH_BINARY)
    white_pixels = cv2.countNonZero(threshold)
    logger.debug(f'White: {white_pixels}, Total: {roi_pixels}, Pct: {white_pixels / roi_pixels}')

    # Check if there are enough black pixels to confirm a selection
    return (white_pixels / roi_pixels) < CHECKBOX_WHITE_PIXEL_THRESHOLD


def should_copy_from_previous(ocr_text: str) -> bool:
    # TODO: Be smarter about this
    copy_values = ['11', '=', '"']
    return any([value in ocr_text for value in copy_values])


def extract_identifier(
    identifier_regex: str | None,
    text: str,
) -> int | None:
    if identifier_regex is None:
        logger.error('Attempt to extract identifier with no regex')
        return None

    # Enforce constraint that the regex has a named group called "id"
    regex_pattern = re.compile(identifier_regex)
    if 'id' not in list(regex_pattern.groupindex.keys()):
        logger.error(f'Identifier regex did not have a capture group named <id>: {identifier_regex}')
        return None

    regex_match = regex_pattern.match(text)
    if regex_match is None:
        logger.error(f'Identifier regex did not match: "{text}" - "{identifier_regex}"')
        return None

    identifier_str = regex_match.group('id')
    try:
        identifier = int(identifier_str)
        logger.info(f'Identifier found: {identifier}')
        return identifier
    except ValueError:
        logger.error(f'Identifier could not be converted to an integer: "{identifier_str}"')
        return None


def locate_linked_field(
        link_method: FormLinkingMethod,
        current_field: TextField,
        current_region: ProcessedRegion,
        identifier_field: ProcessedTextField | None,
) -> ProcessedTextField | None:
    match link_method:
        case FormLinkingMethod.NO_LINKING:
            logger.error(f'Requested to link "{current_field.name}" but the reference form does not allow linking')
            return None

        case FormLinkingMethod.PREVIOUS_REGION:
            linked_region_id = current_region.local_id - 1
            if linked_region_id < 0:
                logger.error(f'PREVIOUS_REGION: Attempted to link from the first region!')
                return None

            # Try and locate a region with our previous id
            linked_region = current_region.process_result.regions.get(linked_region_id, None)
            if linked_region is None:
                logger.warning(f'PREVIOUS_REGION: Could not locate region with id {linked_region_id}')
                return None

            logger.info(f'Located region with id {linked_region_id} - {linked_region.name}')

            # Find the field that matches us
            matched_fields = [
                field
                for field in linked_region.fields
                if field.text_field and field.text_field.name == current_field.name
            ]
            return matched_fields[0].text_field if matched_fields else None

        case FormLinkingMethod.PREVIOUS_IDENTIFIER:
            assert identifier_field is not None
            # TODO
            return None

        case _:
            logger.error(f'Unknown link method: "{link_method.name}"')
            return None
