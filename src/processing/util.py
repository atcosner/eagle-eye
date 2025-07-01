import cv2
import numpy as np
from pathlib import Path
from typing import NamedTuple, Any


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


def rotate_image(image: np.array, degrees: float) -> np.array:
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

    # Order the marks in left-to-right and top-to-bottom order
    marks_x_sort = sorted(alignment_marks, key=lambda m: m.x)
    left_marks = sorted(marks_x_sort[:len(marks_x_sort)//2], key=lambda m: m.y)
    right_marks = sorted(marks_x_sort[len(marks_x_sort)//2:], key=lambda m: m.y)

    return left_marks + right_marks


def alignment_marks_to_points(marks: list[AlignmentMark]) -> np.array:
    points = []
    for mark in marks:
        points.append((mark.x, mark.y))
        points.append((mark.x + mark.width, mark.y))
        points.append((mark.x, mark.y + mark.height))
        points.append((mark.x + mark.width, mark.y + mark.height))

    return np.array(points, dtype='float')


def group_by_normalized_position(
        list1: list[AlignmentMark],
        list2: list[AlignmentMark],
        max_distance_threshold: float = 0.3,
) -> dict[str, Any] | None:
    """
    Group points based on their normalized position in their respective coordinate spaces.
    Points with similar relative positions are grouped together.

    Args:
        list1, list2: Lists of (x, y) coordinate tuples
        max_distance_threshold: Maximum normalized distance to consider a valid match
                               (0.0 = exact match, 1.0 = opposite corners could match)

    Returns:
        dict with keys:
        - 'matched_pairs': List of (point1, point2) tuples for successfully matched points
        - 'unmatched_list1': Points from list1 that couldn't be matched
        - 'unmatched_list2': Points from list2 that couldn't be matched
        - 'match_distances': List of normalized distances for each match
    """
    def normalize_points(points):
        if not points:
            return []

        if len(points) == 1:
            # Single point gets normalized to (0.5, 0.5) - center
            return [((0.5, 0.5), points[0])]

        xs = [p.x for p in points]
        ys = [p.y for p in points]

        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)

        # Avoid division by zero
        x_range = max_x - min_x if max_x != min_x else 1
        y_range = max_y - min_y if max_y != min_y else 1

        normalized = []
        for point in points:
            norm_x = (point[0] - min_x) / x_range
            norm_y = (point[1] - min_y) / y_range
            normalized.append(((norm_x, norm_y), point))

        return normalized

    # Handle empty lists
    if not list1 or not list2:
        return None

    # Normalize both lists
    norm_list1 = normalize_points(list1)
    norm_list2 = normalize_points(list2)

    # Find best matches using a greedy approach
    matched_pairs = []
    match_distances = []
    used_list2_indices = set()
    unmatched_list1 = []

    for norm_coord1, point1 in norm_list1:
        best_match_idx = None
        best_distance = float('inf')

        # Find the closest available point in list2
        for i, (norm_coord2, point2) in enumerate(norm_list2):
            if i in used_list2_indices:
                continue

            # Calculate Euclidean distance between normalized coordinates
            dist = (
                (norm_coord1[0] - norm_coord2[0])**2 +
                (norm_coord1[1] - norm_coord2[1])**2
            )**0.5

            if dist < best_distance:
                best_distance = dist
                best_match_idx = i

        # Only accept the match if it's within the threshold
        if best_match_idx is not None and best_distance <= max_distance_threshold:
            matched_pairs.append((point1, norm_list2[best_match_idx][1]))
            match_distances.append(best_distance)
            used_list2_indices.add(best_match_idx)
        else:
            unmatched_list1.append(point1)

    # Collect unmatched points from list2
    unmatched_list2 = []
    for i, (norm_coord2, point2) in enumerate(norm_list2):
        if i not in used_list2_indices:
            unmatched_list2.append(point2)

    return {
        'matched_pairs': matched_pairs,
        'unmatched_list1': unmatched_list1,
        'unmatched_list2': unmatched_list2,
        'match_distances': match_distances
    }
