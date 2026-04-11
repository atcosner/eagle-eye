import cv2
import logging
import numpy as np
from pathlib import Path
from sqlalchemy.orm import Session

from src.database.pre_processing.pre_process_result import PreProcessResult
from src.database.pre_processing.rotation_attempt import RotationAttempt
from src.util.logging import NamedLoggerAdapter
from src.util.status import FileStatus

from .util import (
    AlignmentMark, find_alignment_marks, rotate_image, group_by_normalized_position, alignment_marks_to_points,
)

# Allow for an image to be +/- 4 degrees rotated
# TODO: Control this with a user setting
ALLOWED_ROTATIONS = [0] \
                    + list(np.arange(0.5, 4.0, 0.5)) \
                    + list(np.arange(-0.5, -4.0, -0.5))

# configuration for automatic alignment
MAX_FEATURES = 500
KEYPOINT_KEEP_THRESHOLD = 0.2   # top 20% of keypoints
MIN_INLIER_RATIO = 0.15         # RANSAC inliers as a fraction of kept matches
                                 # (kept low because handwriting features on the test image
                                 # can never match the blank reference and are always outliers)
MIN_INLIER_Y_COVERAGE = 0.5     # inliers must span at least 50% of the image height;
                                 # a narrow band of inliers means the bottom is extrapolated
MIN_ALIGNMENT_NCC = 0.5         # minimum normalized cross-correlation between aligned and reference


class AlignmentError(Exception):
    pass


class AlignmentFailed(Exception):
    pass


def build_image_paths(directory: Path) -> tuple[Path, Path, Path]:
    return directory / 'matches.png', directory / 'aligned.png', directory / 'overlaid.png'


def reference_mark_alignment(
        logger: logging.Logger | NamedLoggerAdapter,
        session: Session,
        working_directory: Path,
        reference_image: np.ndarray,
        test_image: np.ndarray,
        alignment_mark_count: int,
        result: PreProcessResult,
) -> FileStatus:
    matches_path, aligned_path, overlaid_path = build_image_paths(working_directory)

    # Find the alignment marks in the reference image
    reference_alignment_marks = find_alignment_marks(reference_image)
    logger.info(
        f'Reference Image: Found {len(reference_alignment_marks)} marks, '
        f'expected {alignment_mark_count}'
    )
    if len(reference_alignment_marks) != alignment_mark_count:
        logger.error(f'Failed to find the correct number of alignment marks in the reference form')
        logger.error(f'Found {len(reference_alignment_marks)}, expected {alignment_mark_count}')
        raise AlignmentError()

    # Work through each rotation angle and check for alignment marks
    detected_marks: dict[float, list[AlignmentMark]] = {}
    for rotation_angle in ALLOWED_ROTATIONS:
        # Rotate the image
        rotated_image = test_image
        if rotation_angle != 0:
            rotated_image = rotate_image(rotated_image, rotation_angle)

        alignment_marks = find_alignment_marks(rotated_image)
        logger.info(f'Rotation Result: {rotation_angle} degrees, {len(alignment_marks)} alignment marks')
        detected_marks[rotation_angle] = alignment_marks

        # draw found alignment marks on the file
        color_rotation_image = cv2.cvtColor(rotated_image, cv2.COLOR_GRAY2BGR)
        for mark in alignment_marks:
            start = (mark.x, mark.y)
            end = (mark.x + mark.width, mark.y + mark.height)
            cv2.rectangle(color_rotation_image, start, end, (0, 0, 255), 2)

        rotated_path = working_directory / f'rotation_{rotation_angle}.png'
        cv2.imwrite(str(rotated_path), color_rotation_image)

        # Save the attempt in the DB
        result.rotation_attempts[rotation_angle] = RotationAttempt(
            rotation_angle=rotation_angle,
            path=rotated_path,
        )

    session.commit()

    # Chose the best rotation that found all the alignment marks
    best_angle: float | None = None
    best_angle_marks: list[AlignmentMark] | None = None
    for angle, marks in detected_marks.items():
        if best_angle is None or len(marks) >= len(best_angle_marks):
            # only accept equal marks if the angle is closer to 0
            if best_angle_marks is None or len(marks) != len(best_angle_marks) or abs(angle) < abs(best_angle):
                logger.info(f'New best angle: {angle} ({len(marks)} marks)')
                best_angle = angle
                best_angle_marks = marks

    logger.info(f'Best rotation angle: {best_angle} degrees ({len(best_angle_marks)} marks)')
    if best_angle is None:
        raise AlignmentFailed()

    result.alignment_possible = True
    result.accepted_rotation_angle = best_angle

    # Filter down the reference alignment marks if we didn't find them all in the test image
    if len(best_angle_marks) != alignment_mark_count:
        match_result = group_by_normalized_position(
            best_angle_marks,
            reference_alignment_marks
        )
        # print(match_result)
        test_points, ref_points = zip(*match_result['matched_pairs'])
        best_angle_marks = list(test_points)
        reference_alignment_marks = list(ref_points)

    # Convert the alignment marks to matchpoints
    input_matchpoints = alignment_marks_to_points(best_angle_marks)
    ref_matchpoints = alignment_marks_to_points(reference_alignment_marks)

    # Save an image of the matches
    input_image_rotated = rotate_image(test_image, best_angle)
    matched_image = cv2.drawMatches(
        input_image_rotated,
        [cv2.KeyPoint(x, y, 2) for x, y in input_matchpoints],
        reference_image,
        [cv2.KeyPoint(x, y, 2) for x, y in ref_matchpoints],
        [cv2.DMatch(x, x, 1) for x in range(len(ref_matchpoints))],
        None,
    )
    logger.info(f'Writing matches image: {matches_path}')
    cv2.imwrite(str(matches_path), matched_image)
    result.matches_image_path = matches_path

    # Compute the homography matrix and align the images using it
    (matrix_h, _) = cv2.findHomography(input_matchpoints, ref_matchpoints, method=cv2.RANSAC)
    (h, w) = reference_image.shape[:2]
    aligned_image = cv2.warpPerspective(input_image_rotated, matrix_h, (w, h))
    logger.info(f'Writing aligned image: {aligned_path}')
    cv2.imwrite(str(aligned_path), aligned_image)
    result.aligned_image_path = aligned_path

    # Save an overlaid image to assist in debugging
    overlaid_image = aligned_image.copy()
    cv2.addWeighted(reference_image, 0.5, aligned_image, 0.5, 0, overlaid_image)
    logger.info(f'Writing overlaid image: {overlaid_path}')
    cv2.imwrite(str(overlaid_path), overlaid_image)
    result.overlaid_image_path = overlaid_path

    # Determine if this was a full or partial success
    if len(best_angle_marks) != alignment_mark_count:
        status = FileStatus.WARNING
        result.fully_aligned = False
    else:
        status = FileStatus.SUCCESS
        result.fully_aligned = True

    # commit to the DB and signal out we are done
    session.commit()
    return status


def _compute_ncc(img1: np.ndarray, img2: np.ndarray) -> float:
    """Compute the normalized cross-correlation between two same-shape images.

    Returns a value in [-1, 1] where 1.0 is a perfect match.
    """
    a = img1.astype(np.float64) - img1.mean()
    b = img2.astype(np.float64) - img2.mean()
    denominator = np.sqrt((a ** 2).sum() * (b ** 2).sum())
    if denominator == 0:
        return 0.0
    return float(np.sum(a * b) / denominator)


def automatic_alignment(
        logger: logging.Logger | NamedLoggerAdapter,
        session: Session,
        working_directory: Path,
        reference_image: np.ndarray,
        test_image: np.ndarray,
        result: PreProcessResult,
) -> FileStatus:
    matches_path, aligned_path, overlaid_path = build_image_paths(working_directory)

    # detect keypoints and extract features
    orb = cv2.ORB_create(MAX_FEATURES)
    ref_keypoints, ref_descriptors = orb.detectAndCompute(reference_image, None)
    test_keypoints, test_descriptors = orb.detectAndCompute(test_image, None)
    logger.info(f'Found {len(ref_keypoints)} reference keypoints and {len(test_keypoints)} test keypoints')

    # match the features
    matcher = cv2.DescriptorMatcher_create(cv2.DESCRIPTOR_MATCHER_BRUTEFORCE_HAMMING)
    matches = matcher.match(test_descriptors, ref_descriptors, None)
    matches = sorted(matches, key=lambda x:x.distance)
    logger.info(f'Found {len(matches)} matches')

    # keep only the top matches
    keep = int(len(matches) * KEYPOINT_KEEP_THRESHOLD)
    matches = matches[:keep]
    logger.info(f'Truncated matches to {len(matches)} ({KEYPOINT_KEEP_THRESHOLD:.2%})')

    # save off an image of the matches
    matched_image = cv2.drawMatches(
        test_image,
        test_keypoints,
        reference_image,
        ref_keypoints,
        matches,
        None,
    )
    logger.info(f'Writing matches image: {matches_path}')
    cv2.imwrite(str(matches_path), matched_image)
    result.matches_image_path = matches_path

    # prep the keypoints to compute an affine matrix
    test_points = np.zeros((len(matches), 2), dtype="float")
    ref_points = np.zeros((len(matches), 2), dtype="float")
    for (idx, match) in enumerate(matches):
        test_points[idx] = test_keypoints[match.queryIdx].pt
        ref_points[idx] = ref_keypoints[match.trainIdx].pt

    # Default some fields in the result before we start the alignment
    result.alignment_possible = False
    result.fully_aligned = False

    # Estimate an affine (not perspective/homography) transform.
    # A full homography has 8 DOF and can model perspective warp, which causes distortion
    # in regions away from where features are concentrated.  For two scans of the same
    # flat document the correct transform is affine (6 DOF: translate + rotate + scale +
    # shear), which cannot introduce that kind of warp.
    (matrix_aff, ransac_mask) = cv2.estimateAffine2D(test_points, ref_points, method=cv2.RANSAC)

    # Check 1: estimateAffine2D returns None when it cannot find a valid solution.
    # This is the only check that prevents saving — without a matrix there is nothing to warp.
    if matrix_aff is None:
        logger.error('estimateAffine2D failed to compute a valid affine matrix')
        session.commit()
        return FileStatus.FAILED
    
    # If we got a transform matrix, mark the image as possible to align
    result.alignment_possible = True

    # Checks 2 and 3 evaluate whether the computed matrix is trustworthy, but we still
    # warp and save the images afterwards so the user can inspect a bad alignment and
    # report it as a bug or future improvement.
    alignment_failed = False

    # Check 2: a low RANSAC inlier ratio means the match set was too noisy to trust
    inlier_count = int(ransac_mask.sum())
    inlier_ratio = inlier_count / len(matches)
    logger.info(f'RANSAC inliers: {inlier_count}/{len(matches)} ({inlier_ratio:.2%})')
    if inlier_ratio < MIN_INLIER_RATIO:
        logger.error(
            f'RANSAC inlier ratio {inlier_ratio:.2%} is below the minimum threshold '
            f'({MIN_INLIER_RATIO:.2%}) — alignment is unreliable'
        )
        alignment_failed = True

    # Check 3: inliers must be spread across the image height, not clustered in one band.
    # If all good matches are near the top, the affine transform is reliable there but
    # the bottom is a blind extrapolation.
    inlier_pts = test_points[ransac_mask.ravel() == 1]
    y_coverage = (inlier_pts[:, 1].max() - inlier_pts[:, 1].min()) / test_image.shape[0]
    logger.info(f'Inlier vertical coverage: {y_coverage:.2%} (threshold: {MIN_INLIER_Y_COVERAGE:.2%})')
    if y_coverage < MIN_INLIER_Y_COVERAGE:
        logger.error(
            f'Inliers only cover {y_coverage:.2%} of image height — '
            f'alignment below the matched region is unreliable'
        )
        alignment_failed = True

    # Always warp and save so the user can inspect the result regardless of quality
    (h, w) = reference_image.shape[:2]
    aligned_image = cv2.warpAffine(test_image, matrix_aff, (w, h))
    logger.info(f'Writing aligned image: {aligned_path}')
    cv2.imwrite(str(aligned_path), aligned_image)
    result.aligned_image_path = aligned_path

    overlaid_image = aligned_image.copy()
    cv2.addWeighted(reference_image, 0.5, aligned_image, 0.5, 0, overlaid_image)
    logger.info(f'Writing overlaid image: {overlaid_path}')
    cv2.imwrite(str(overlaid_path), overlaid_image)
    result.overlaid_image_path = overlaid_path

    if alignment_failed:
        session.commit()
        return FileStatus.FAILED

    # Check 4: compare the aligned image to the reference with NCC to catch cases where
    # the transform was computed successfully but the visual result is wrong
    ncc = _compute_ncc(reference_image, aligned_image)
    logger.info(f'Post-alignment NCC: {ncc:.4f} (threshold: {MIN_ALIGNMENT_NCC})')
    if ncc < MIN_ALIGNMENT_NCC:
        logger.error(
            f'Post-alignment NCC {ncc:.4f} is below the minimum threshold '
            f'({MIN_ALIGNMENT_NCC}) — images do not appear to be aligned'
        )
        session.commit()
        return FileStatus.WARNING

    # Indicate a sucessful alignment if we passed all the quality checks
    result.fully_aligned = True
    session.commit()
    return FileStatus.SUCCESS
