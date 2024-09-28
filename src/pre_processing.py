import cv2
import logging
import numpy as np
from pathlib import Path
from typing import NamedTuple

from .definitions.forms import ReferenceForm

# Allow for an image to be +/- 6 degrees rotated
ROTATION_ATTEMPTS = [0] + list(range(1, 6, 1)) + list(range(-1, -6, -1))

logger = logging.getLogger(__name__)


class AlignmentResult(NamedTuple):
    test_image_path: Path
    matched_features_image_path: Path
    overlaid_image_path: Path
    aligned_image_path: Path


class AlignmentMark(NamedTuple):
    x: int
    y: int
    height: int
    width: int


def grayscale_image(image_path: Path) -> Path:
    assert image_path.exists(), f'Image did not exist: {image_path}'

    image = cv2.imread(str(image_path))
    image_grayscale = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    output_path = image_path.parent / f'grayscale_image{image_path.suffix}'
    cv2.imwrite(str(output_path), image_grayscale)
    return output_path


def rotate_image(image: np.array, degrees: int) -> np.array:
    image_center = tuple(np.array(image.shape[1::-1]) / 2)
    rot_mat = cv2.getRotationMatrix2D(image_center, degrees, 1.0)
    return cv2.warpAffine(image, rot_mat, image.shape[1::-1], flags=cv2.INTER_LINEAR)


def detect_alignment_marks(image: np.array, expected_marks: int) -> tuple[np.array, list[AlignmentMark]]:
    found_marks: tuple[int, list[AlignmentMark]] | None = None
    for attempt_degrees in ROTATION_ATTEMPTS:
        logger.info(f'Trying {attempt_degrees} degree rotation')

        # Grayscale and rotate if required
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        if attempt_degrees != 0:
            gray = rotate_image(gray, attempt_degrees)

        # Threshold to eliminate noise
        _, threshold = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        # Find all possible contours in the image
        marks = []
        contours, _ = cv2.findContours(threshold, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        for c in contours:
            x, y, width, height = cv2.boundingRect(c)
            side_ratio = height / width

            contour_roi = threshold[y:y + height, x:x + width]
            white_pixels = cv2.countNonZero(contour_roi)
            color_ratio = white_pixels / (height * width)

            # Check that the mark is mostly square and contains almost all black pixels
            if (0.9 < side_ratio < 1.1) and (color_ratio < 0.2):
                marks.append(AlignmentMark(x, y, height, width))

        logger.info(f'Found {len(marks)} marks')
        if len(marks) == expected_marks:
            found_marks = (attempt_degrees, marks)
            break

    if found_marks is None:
        raise RuntimeError('Failed to detect alignment marks')

    best_rotation, marks = found_marks
    logger.info(f'Using a rotation of {best_rotation} degrees found {len(marks)} alignment marks')

    # Order the marks in left-to-right and top-to-bottom order
    marks_x_sort = sorted(marks, key=lambda m: m.x)
    left_marks = sorted(marks_x_sort[:len(marks_x_sort)//2], key=lambda m: m.y)
    right_marks = sorted(marks_x_sort[len(marks_x_sort)//2:], key=lambda m: m.y)

    # Rotate the image and return the alignment marks
    rotated_image = rotate_image(image, best_rotation)
    return rotated_image, left_marks + right_marks


def alignment_marks_to_points(marks: list[AlignmentMark]) -> np.array:
    points = []
    for mark in marks:
        points.append((mark.x, mark.y))
        points.append((mark.x + mark.width, mark.y))
        points.append((mark.x, mark.y + mark.height))
        points.append((mark.x + mark.width, mark.y + mark.height))

    return np.array(points, dtype='float')


def align_images(
        test_image_path: Path,
        reference_form: ReferenceForm,
) -> AlignmentResult:
    assert test_image_path.exists(), f'Test image did not exist: {test_image_path}'
    assert reference_form.path.exists(), f'Ref image did not exist: {reference_form.path}'

    matched_image_path = test_image_path.parent / f'matched_image{test_image_path.suffix}'
    aligned_image_path = test_image_path.parent / f'aligned_image{test_image_path.suffix}'
    overlaid_image_path = test_image_path.parent / f'overlaid_image{test_image_path.suffix}'

    test_image = cv2.imread(str(test_image_path))
    reference_image = cv2.imread(str(reference_form.path))

    # Detect alignment marks in both images
    test_image_rotate, test_marks = detect_alignment_marks(test_image, reference_form.reference_marks_count)
    _, reference_marks = detect_alignment_marks(reference_image, reference_form.reference_marks_count)

    # Convert the alignment marks to matchpoints
    test_matchpoints = alignment_marks_to_points(test_marks)
    ref_matchpoints = alignment_marks_to_points(reference_marks)

    # Save an image of the matches
    matched_image = cv2.drawMatches(
        test_image_rotate,
        [cv2.KeyPoint(x, y, 2) for x, y in test_matchpoints],
        reference_image,
        [cv2.KeyPoint(x, y, 2) for x, y in ref_matchpoints],
        [cv2.DMatch(x, x, 1) for x in range(len(ref_matchpoints))],
        None,
    )
    cv2.imwrite(str(matched_image_path), matched_image)

    # Compute the homography matrix and align the images using it
    (H, _) = cv2.findHomography(test_matchpoints, ref_matchpoints, method=cv2.RANSAC)
    (h, w) = reference_image.shape[:2]
    aligned_image = cv2.warpPerspective(test_image_rotate, H, (w, h))
    cv2.imwrite(str(aligned_image_path), aligned_image)

    # Save an overlaid image to assist in debugging
    overlaid_image = aligned_image.copy()
    cv2.addWeighted(reference_image, 0.5, aligned_image, 0.5, 0, overlaid_image)
    cv2.imwrite(str(overlaid_image_path), overlaid_image)

    return AlignmentResult(
        test_image_path=test_image_path,
        matched_features_image_path=matched_image_path,
        overlaid_image_path=overlaid_image_path,
        aligned_image_path=aligned_image_path,
    )
