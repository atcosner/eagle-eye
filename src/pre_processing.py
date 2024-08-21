import cv2
import numpy as np
from pathlib import Path
from typing import NamedTuple


class AlignmentResult(NamedTuple):
    test_image_path: Path
    matched_features_image_path: Path
    overlaid_image_path: Path
    aligned_image_path: Path


def grayscale_image(image_path: Path) -> Path:
    assert image_path.exists(), f'Image did not exist: {image_path}'

    image = cv2.imread(str(image_path))
    image_grayscale = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    output_path = image_path.parent / f'grayscale_image{image_path.suffix}'
    cv2.imwrite(str(output_path), image_grayscale)
    return output_path


def align_images(
        test_image_path: Path,
        reference_image_path: Path,
        max_features: int = 1000,
        match_keep_percent: float = 0.2,
) -> AlignmentResult:
    assert test_image_path.exists(), f'Test image did not exist: {test_image_path}'
    assert reference_image_path.exists(), f'Ref image did not exist: {reference_image_path}'

    matched_image_path = test_image_path.parent / f'matched_image{test_image_path.suffix}'
    aligned_image_path = test_image_path.parent / f'aligned_image{test_image_path.suffix}'
    overlaid_image_path = test_image_path.parent / f'overlaid_image{test_image_path.suffix}'

    test_image = cv2.imread(str(test_image_path))
    reference_image = cv2.imread(str(reference_image_path))

    # Detect keypoints and compute features
    orb = cv2.ORB_create(max_features)
    test_keypoints, test_features = orb.detectAndCompute(test_image, None)
    ref_keypoints, ref_features = orb.detectAndCompute(reference_image, None)

    # Match the features and sort by distance
    matcher = cv2.DescriptorMatcher_create(cv2.DESCRIPTOR_MATCHER_BRUTEFORCE_HAMMING)
    matches = sorted(matcher.match(test_features, ref_features, None), key=lambda x: x.distance)

    # Truncate matches and save an image of the matches
    matches = matches[:int(len(matches) * match_keep_percent)]
    matched_image = cv2.drawMatches(test_image, test_keypoints, reference_image, ref_keypoints, matches, None)
    cv2.imwrite(str(matched_image_path), matched_image)

    # Populate numpy arrays for the matched points
    test_matchpoints = np.zeros((len(matches), 2), dtype='float')
    ref_matchpoints = np.zeros((len(matches), 2), dtype='float')
    for (i, m) in enumerate(matches):
        test_matchpoints[i] = test_keypoints[m.queryIdx].pt
        ref_matchpoints[i] = ref_keypoints[m.trainIdx].pt

    # Compute the homography matrix and align the images using it
    (H, _) = cv2.findHomography(test_matchpoints, ref_matchpoints, method=cv2.RANSAC)
    (h, w) = reference_image.shape[:2]
    aligned_image = cv2.warpPerspective(test_image, H, (w, h))
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

