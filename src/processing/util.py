import cv2
import numpy as np
from pathlib import Path
from typing import NamedTuple


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


def find_alignment_marks(image: np.array) -> list[AlignmentMark]:
    alignment_marks = []
    contours, _ = cv2.findContours(image, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    for c in contours:
        x, y, width, height = cv2.boundingRect(c)
        side_ratio = height / width

        contour_roi = image[y:y + height, x:x + width]
        white_pixels = cv2.countNonZero(contour_roi)
        color_ratio = white_pixels / (height * width)

        # Check that the mark is mostly square and contains almost all black pixels
        if (0.9 < side_ratio < 1.1) and (color_ratio < 0.2):
            alignment_marks.append(AlignmentMark(x, y, height, width))

    return alignment_marks


def alignment_marks_to_points(marks: list[AlignmentMark]) -> np.array:
    points = []
    for mark in marks:
        points.append((mark.x, mark.y))
        points.append((mark.x + mark.width, mark.y))
        points.append((mark.x, mark.y + mark.height))
        points.append((mark.x + mark.width, mark.y + mark.height))

    return np.array(points, dtype='float')
