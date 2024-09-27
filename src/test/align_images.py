import cv2
import imutils
import numpy as np
from enum import Enum, auto
from pathlib import Path
from typing import NamedTuple


ROTATION_ATTEMPTS = [0] + list(range(1, 6, 1)) + list(range(-1, -6, -1))


class MarkLocation(Enum):
    LEFT_TOP = auto()
    LEFT_MIDDLE_UPPER = auto()
    LEFT_MIDDLE_LOWER = auto()
    LEFT_BOTTOM = auto()
    RIGHT_TOP = auto()
    RIGHT_MIDDLE_UPPER = auto()
    RIGHT_MIDDLE_LOWER = auto()
    RIGHT_BOTTOM = auto()


class AlignmentMark(NamedTuple):
    x: int
    y: int
    height: int
    width: int


def rotate_image(image: np.array, degrees: int) -> np.array:
    image_center = tuple(np.array(image.shape[1::-1]) / 2)
    rot_mat = cv2.getRotationMatrix2D(image_center, degrees, 1.0)
    return cv2.warpAffine(image, rot_mat, image.shape[1::-1], flags=cv2.INTER_LINEAR)


def detect_alignment_marks(image: np.array) -> tuple[np.array, list[AlignmentMark]]:
    found_marks: tuple[int, list[AlignmentMark]] | None = None
    for attempt_degrees in ROTATION_ATTEMPTS:
        print(f'Trying {attempt_degrees} degree rotation')

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

        print(f'Found {len(marks)} marks')
        if len(marks) == 16:
            found_marks = (attempt_degrees, marks)
            break

    # TODO: Require at least X marks to continue
    if found_marks is None:
        raise RuntimeError('Failed to detect alignment marks')

    best_rotation, marks = found_marks
    print(f'Using a rotation of {best_rotation} degrees found {len(marks)} alignment marks')

    # Order the marks in left-to-right and top-to-bottom order
    marks_x_sort = sorted(marks, key=lambda m: m.x)
    sorted_marks = sorted(marks_x_sort[:len(marks)//2], key=lambda m: m.y) + sorted(marks_x_sort[len(marks)//2:], key=lambda m: m.y)

    # Rotate the image and return the alignment marks
    rotated_image = rotate_image(image, best_rotation)
    return rotated_image, sorted_marks


def align_images(
        test: np.array,
        test_align_marks: list[AlignmentMark],
        reference: np.array,
        reference_align_marks: list[AlignmentMark],
        max_keypoint_regions: int = 1000,
        match_keep_percent: float = 0.2,
        show_matches: bool = False,
) -> np.array:
    # Ensure both images are in grayscale
    test_grayscale = cv2.cvtColor(test, cv2.COLOR_BGR2GRAY)
    reference_grayscale = cv2.cvtColor(reference, cv2.COLOR_BGR2GRAY)

    _, test_grayscale = cv2.threshold(test_grayscale, 127, 255, 0)
    _, reference_grayscale = cv2.threshold(reference_grayscale, 127, 255, 0)

    # # Detect keypoints and compute features
    # orb = cv2.ORB_create(max_keypoint_regions)
    # (test_keypoints, test_features) = orb.detectAndCompute(test_grayscale, None)  #, test_mask)
    # (ref_keypoints, ref_features) = orb.detectAndCompute(reference_grayscale, None)  #, reference_mask)
    #
    # test1 = cv2.drawKeypoints(test_grayscale, test_keypoints, 0, flags=cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
    # cv2.imshow('Test', imutils.resize(test1, width=500))
    # cv2.waitKey(0)
    # test1 = cv2.drawKeypoints(reference_grayscale, ref_keypoints, 0, flags=cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
    # cv2.imshow('Reference', imutils.resize(test1, width=500))
    # cv2.waitKey(0)
    #
    # # Match the features and sort by distance
    # matcher = cv2.DescriptorMatcher_create(cv2.DESCRIPTOR_MATCHER_BRUTEFORCE_HAMMING)
    # matches = sorted(matcher.match(test_features, ref_features, None), key=lambda x: x.distance)
    #
    # # Truncate to only the top X percent
    # matches = matches[:int(len(matches) * match_keep_percent)]
    # if show_matches:
    #     matches_img = cv2.drawMatches(test, test_keypoints, reference, ref_keypoints, matches, None)
    #     cv2.imshow('Matched Keypoints', imutils.resize(matches_img, width=1000))
    #     cv2.waitKey(0)
    #
    # # Populate numpy arrays for the matched points
    # test_matchpoints = np.zeros((len(matches), 2), dtype='float')
    # ref_matchpoints = np.zeros((len(matches), 2), dtype='float')
    # for (i, m) in enumerate(matches):
    #     test_matchpoints[i] = test_keypoints[m.queryIdx].pt
    #     ref_matchpoints[i] = ref_keypoints[m.trainIdx].pt
    #
    # print(test_matchpoints)
    # print(ref_matchpoints)

    test_points = []
    for mark in test_align_marks:
        test_points += [
            (mark.x, mark.y),
            (mark.x + mark.width, mark.y),
            (mark.x, mark.y + mark.height),
            (mark.x + mark.width, mark.y + mark.height),
        ]

    ref_points = []
    for mark in reference_align_marks:
        ref_points += [
            (mark.x, mark.y),
            (mark.x + mark.width, mark.y),
            (mark.x, mark.y + mark.height),
            (mark.x + mark.width, mark.y + mark.height),
        ]

    ref_matchpoints = np.array(ref_points, dtype='float')
    test_matchpoints = np.array(test_points, dtype='float')
    (h, w) = reference.shape[:2]

    # Draw and show the matched image
    test_keypoints = [cv2.KeyPoint(x, y, 2) for x, y in test_points]
    ref_keypoints = [cv2.KeyPoint(x, y, 2) for x, y in ref_points]
    matches = [cv2.DMatch(x, x, 1) for x in range(len(ref_matchpoints))]
    matches_img = cv2.drawMatches(test, test_keypoints, reference, ref_keypoints, matches, None)
    cv2.imshow('Matched', imutils.resize(matches_img, width=500))
    cv2.waitKey(0)

    # Compute the homography matrix and align the images using it
    (H, _) = cv2.findHomography(test_matchpoints, ref_matchpoints, method=cv2.RANSAC)
    return cv2.warpPerspective(test, H, (w, h))

    # print(ref_matchpoints)
    # warp_mat = cv2.getAffineTransform(test_matchpoints, ref_matchpoints)
    # return cv2.warpAffine(test, warp_mat, (w, h), flags=cv2.INTER_LINEAR)


if __name__ == '__main__':
    resource_path = Path.cwd() / '..' / '..' / 'forms'

    # Load the dev and production images
    test_img = cv2.imread(str(resource_path / 'dev' / 'test_kt_form__filled_errors.jpg'))
    reference_img = cv2.imread(str(resource_path / 'production' / 'kt_field_form_v8.png'))

    test_img, test_marks = detect_alignment_marks(test_img)
    reference_img, reference_marks = detect_alignment_marks(reference_img)

    # Align them
    aligned_img = align_images(test_img, test_marks, reference_img, reference_marks, show_matches=True)

    aligned_img = imutils.resize(aligned_img, width=500)
    reference_img = imutils.resize(reference_img, width=500)
    stacked = np.hstack([aligned_img, reference_img])

    overlay = reference_img.copy()
    output = aligned_img.copy()
    cv2.addWeighted(overlay, 0.5, output, 0.5, 0, output)
    cv2.imshow("Image Alignment Stacked", stacked)
    cv2.imshow("Image Alignment Overlay", output)
    cv2.waitKey(0)
