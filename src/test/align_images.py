import cv2
import imutils
import numpy as np
from pathlib import Path


def create_alignment_mask(image) -> np.array:
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, threshold = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    mask = np.zeros(gray.shape[:2], dtype=np.uint8)

    contours, _ = cv2.findContours(threshold, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    for c in contours:
        x, y, width, height = cv2.boundingRect(c)
        side_ratio = height / width

        contour_roi = threshold[y:y + height, x:x + width]
        white_pixels = cv2.countNonZero(contour_roi)
        color_ratio = white_pixels / (height * width)

        if (0.9 < side_ratio < 1.1) and (color_ratio < 0.2):
            cv2.rectangle(image, (x, y), (x + width, y + height), (36, 255, 12), 3)
            cv2.rectangle(mask, (x, y), (x + width, y + height), 255, thickness=-1)

    return mask


def align_images(
        test: np.array,
        test_mask: np.array,
        reference: np.array,
        reference_mask: np.array,
        max_keypoint_regions: int = 1000,
        match_keep_percent: float = 0.2,
        show_matches: bool = False,
) -> np.array:
    # Ensure both images are in grayscale
    test_grayscale = cv2.cvtColor(test, cv2.COLOR_BGR2GRAY)
    reference_grayscale = cv2.cvtColor(reference, cv2.COLOR_BGR2GRAY)

    _, test_grayscale = cv2.threshold(test_grayscale, 127, 255, 0)
    _, reference_grayscale = cv2.threshold(reference_grayscale, 127, 255, 0)

    # Detect keypoints and compute features
    orb = cv2.ORB_create(max_keypoint_regions)
    (test_keypoints, test_features) = orb.detectAndCompute(test_grayscale, test_mask)
    (ref_keypoints, ref_features) = orb.detectAndCompute(reference_grayscale, reference_mask)

    test1 = cv2.drawKeypoints(test_grayscale, test_keypoints, 0, flags=cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
    cv2.imshow('Test', imutils.resize(test1, width=500))
    cv2.waitKey(0)
    test1 = cv2.drawKeypoints(reference_grayscale, ref_keypoints, 0, flags=cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
    cv2.imshow('Reference', imutils.resize(test1, width=500))
    cv2.waitKey(0)

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
    resource_path = Path.cwd() / '..' / '..' / 'forms'

    # Load the dev and production images
    test_img = cv2.imread(str(resource_path / 'production' / 'form1__filled.png'))
    reference_img = cv2.imread(str(resource_path / 'production' / 'ku_collection_form_template.png'))

    test_mask = create_alignment_mask(test_img)
    reference_mask = create_alignment_mask(reference_img)

    # Align them
    aligned_img = align_images(test_img, test_mask, reference_img, reference_mask, show_matches=True)

    aligned_img = imutils.resize(aligned_img, width=700)
    reference_img = imutils.resize(reference_img, width=700)
    stacked = np.hstack([aligned_img, reference_img])

    overlay = reference_img.copy()
    output = aligned_img.copy()
    cv2.addWeighted(overlay, 0.5, output, 0.5, 0, output)
    cv2.imshow("Image Alignment Stacked", stacked)
    cv2.imshow("Image Alignment Overlay", output)
    cv2.waitKey(0)
