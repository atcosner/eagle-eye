import cv2
import imutils
import numpy as np
from pathlib import Path


def align_images(
        test: np.array,
        reference: np.array,
        max_keypoint_regions: int = 500,
        match_keep_percent: float = 0.2,
        show_matches: bool = False,
) -> np.array:
    # Ensure both images are in grayscale
    test_grayscale = cv2.cvtColor(test, cv2.COLOR_BGR2GRAY)
    reference_grayscale = cv2.cvtColor(reference, cv2.COLOR_BGR2GRAY)

    # Detect keypoints and compute features
    orb = cv2.ORB_create(max_keypoint_regions)
    (test_keypoints, test_features) = orb.detectAndCompute(test_grayscale, None)
    (ref_keypoints, ref_features) = orb.detectAndCompute(reference_grayscale, None)

    # Match the features and sort by distance
    matcher = cv2.DescriptorMatcher_create(cv2.DESCRIPTOR_MATCHER_BRUTEFORCE_HAMMING)
    matches = sorted(matcher.match(test_features, ref_features, None), key=lambda x: x.distance)

    # Truncate to only the top X percent
    matches = matches[:int(len(matches) * match_keep_percent)]
    if show_matches:
        matches_img = cv2.drawMatches(test, test_keypoints, reference, ref_keypoints, matches, None)
        cv2.imshow('Matched Keypoints', imutils.resize(matches_img, width=1000))
        cv2.waitKey(0)

    # Populate numpy arrays for the matched points
    test_matchpoints = np.zeros((len(matches), 2), dtype='float')
    ref_matchpoints = np.zeros((len(matches), 2), dtype='float')
    for (i, m) in enumerate(matches):
        test_matchpoints[i] = test_keypoints[m.queryIdx].pt
        ref_matchpoints[i] = ref_keypoints[m.trainIdx].pt

    # Compute the homography matrix and align the images using it
    (H, _) = cv2.findHomography(test_matchpoints, ref_matchpoints, method=cv2.RANSAC)
    (h, w) = reference.shape[:2]
    return cv2.warpPerspective(test, H, (w, h))


if __name__ == '__main__':
    resource_path = Path.cwd() / '..' / 'forms'

    # Load the test and reference images
    test_img = cv2.imread(str(resource_path / 'test' / 'collection_form_test2.png'))
    reference_img = cv2.imread(str(resource_path / 'reference' / 'collection_form_template.png'))

    # Align them
    aligned_img = align_images(test_img, reference_img, show_matches=False)

    aligned_img = imutils.resize(aligned_img, width=700)
    reference_img = imutils.resize(reference_img, width=700)
    stacked = np.hstack([aligned_img, reference_img])

    overlay = reference_img.copy()
    output = aligned_img.copy()
    cv2.addWeighted(overlay, 0.5, output, 0.5, 0, output)
    cv2.imshow("Image Alignment Stacked", stacked)
    cv2.imshow("Image Alignment Overlay", output)
    cv2.waitKey(0)
