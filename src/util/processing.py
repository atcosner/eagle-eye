import cv2
import logging
import numpy as np
from pathlib import Path

from .types import BoxBounds

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
