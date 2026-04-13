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
ALLOWED_ROTATIONS: list[float] = list(np.arange(-4.0, 4.0, 0.5).astype(float))


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
    best_angle_marks: list[AlignmentMark] = []
    for angle, marks in detected_marks.items():
        if best_angle is None or len(marks) >= len(best_angle_marks):
            # only accept equal marks if the angle is closer to 0
            if not best_angle_marks or len(marks) != len(best_angle_marks) or (best_angle is not None and abs(angle) < abs(best_angle)):
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
        grouping_result = group_by_normalized_position(
            best_angle_marks,
            reference_alignment_marks
        )
        if grouping_result is not None:
            test_points, ref_points = zip(*grouping_result['matched_pairs'])
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


def _extract_structure_mask(image: np.ndarray) -> np.ndarray:
    """
    Create a mask that emphasizes form structure (horizontal/vertical
    lines, box edges, logger.infoed text baselines) and suppresses areas
    likely to contain only handwriting.
    """
    # Detect edges
    edges = cv2.Canny(image, 50, 150)

    # Morphological operations to emphasize long straight lines

    # Horizontal lines
    h_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (40, 1))
    h_lines = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, h_kernel)

    # Vertical lines
    v_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 40))
    v_lines = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, v_kernel)

    # Combine — areas near structural lines
    structure = cv2.add(h_lines, v_lines)

    # Dilate to create zones around structure for feature detection
    dilate_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (30, 30))
    mask = cv2.dilate(structure, dilate_kernel)

    return mask


def _compute_homography(
        reference_image: np.ndarray,
        test_image: np.ndarray,
        use_structure_mask: bool=True
) -> tuple[np.ndarray | None, int]:
    """
    Compute homography using ORB features, optionally masked to
    structural regions only.
    """
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    ref_e = clahe.apply(reference_image)
    test_e = clahe.apply(test_image)

    # Build structure masks to focus features on form lines/boxes
    ref_mask = None
    test_mask = None
    if use_structure_mask:
        ref_mask = _extract_structure_mask(reference_image)
        test_mask = _extract_structure_mask(test_image)

    orb = cv2.ORB_create(
        nfeatures=15000,
        scaleFactor=1.2,
        nlevels=12,
        edgeThreshold=15,
        patchSize=31,
    )

    kp_r, des_r = orb.detectAndCompute(ref_e, ref_mask)
    kp_t, des_t = orb.detectAndCompute(test_e, test_mask)

    if des_r is None or des_t is None:
        return None, 0

    bf = cv2.BFMatcher(cv2.NORM_HAMMING)
    raw = bf.knnMatch(des_t, des_r, k=2)

    good = []
    for pair in raw:
        if len(pair) == 2:
            m, n = pair
            if m.distance < 0.75 * n.distance:
                good.append(m)

    if len(good) < 10:
        return None, 0

    pts_t = np.float32([kp_t[m.queryIdx].pt for m in good])
    pts_r = np.float32([kp_r[m.trainIdx].pt for m in good])

    # First pass RANSAC
    H, mask = cv2.findHomography(pts_t, pts_r, cv2.RANSAC, 5.0)
    if H is None:
        return None, 0

    inlier_mask = mask.ravel().astype(bool)
    inliers = int(mask.sum())

    # Second pass: recompute homography using only inliers with
    # tighter threshold for refinement
    if inliers >= 10:
        pts_t_in = pts_t[inlier_mask]
        pts_r_in = pts_r[inlier_mask]
        H2, mask2 = cv2.findHomography(pts_t_in, pts_r_in, cv2.RANSAC, 3.0)
        if H2 is not None:
            inliers2 = int(mask2.sum())
            if inliers2 >= 10:
                H = H2
                inliers = inliers2

    return H, inliers


def _create_overlay(
        background: np.ndarray,
        foreground: np.ndarray,
        alpha: float=0.5
) -> np.ndarray:
    h, w = background.shape[:2]
    if foreground.shape[:2] != (h, w):
        foreground = cv2.resize(foreground, (w, h))
    return cv2.addWeighted(background, alpha, foreground, 1 - alpha, 0)


def _create_diff_image(ref_img: np.ndarray, aligned_img: np.ndarray) -> np.ndarray:
    """
    Create a difference image that highlights misalignment.
    Perfectly aligned areas appear gray; misaligned areas show
    the offset in color.
    """
    h, w = ref_img.shape[:2]
    if aligned_img.shape[:2] != (h, w):
        aligned_img = cv2.resize(aligned_img, (w, h))

    diff = cv2.absdiff(ref_img, aligned_img)
    diff = cv2.normalize(diff, None, 0, 255, cv2.NORM_MINMAX)
    diff_color = cv2.applyColorMap(diff, cv2.COLORMAP_JET)

    return diff_color


def automatic_alignment(
        logger: logging.Logger | NamedLoggerAdapter,
        session: Session,
        working_directory: Path,
        reference_image: np.ndarray,
        test_image: np.ndarray,
        result: PreProcessResult,
) -> FileStatus:
    matches_path, aligned_path, overlaid_path = build_image_paths(working_directory)

    # Set some defaults on the result
    result.alignment_possible = False
    result.fully_aligned = False

    h, w = reference_image.shape[:2]
    logger.info(f"Reference : {w}x{h}")
    logger.info(f"Test      : {test_image.shape[1]}x{test_image.shape[0]}")

    # ── Try with structure mask first ──
    logger.info("[1] Computing homography with structure-masked features...")
    H_masked, inliers_masked = _compute_homography(
        reference_image,
        test_image,
        use_structure_mask=True,
    )
    logger.info(f"    Inliers (masked): {inliers_masked}")

    # ── Also try without mask for comparison ──
    logger.info("[2] Computing homography with all features...")
    H_all, inliers_all = _compute_homography(
        reference_image,
        test_image,
        use_structure_mask=False,
    )
    logger.info(f"    Inliers (all):    {inliers_all}")

    # ── Pick the better one ──
    # Prefer masked if it has reasonable inliers, since those features
    # are more likely to be from form structure
    if H_masked is not None and inliers_masked >= 30:
        H = H_masked
        method = "structure-masked"
        inliers = inliers_masked
    elif H_all is not None:
        H = H_all
        method = "all-features"
        inliers = inliers_all
    else:
        raise AlignmentFailed()

    logger.info(f"    Selected: {method} ({inliers} inliers)")
    result.alignment_possible = True

    # ── Warp ──
    aligned_image = cv2.warpPerspective(
        test_image,
        H,
        (w, h),
        flags=cv2.INTER_LINEAR,
        borderMode=cv2.BORDER_CONSTANT,
        borderValue=(255, 255, 255),
    )

    # ── Save outputs ──
    cv2.imwrite(str(aligned_path), aligned_image)
    logger.info(f"Aligned: {aligned_path}")
    result.aligned_image_path = aligned_path

    overlaid_image = _create_overlay(reference_image, aligned_image)
    cv2.imwrite(str(overlaid_path), overlaid_image)
    logger.info(f"Overlaid: {overlaid_path}")
    result.overlaid_image_path = overlaid_path

    diff_image = _create_diff_image(reference_image, aligned_image)
    cv2.imwrite(str(matches_path), diff_image)
    logger.info(f"Difference: {matches_path}")
    result.matches_image_path = matches_path

    # # If both methods worked, save the alternative too for comparison
    # if H_masked is not None and H_all is not None:
    #     alt_H = H_all if method == "structure-masked" else H_masked
    #     alt_aligned_image = cv2.warpPerspective(
    #         test_image,
    #         alt_H,
    #         (w, h),
    #         flags=cv2.INTER_LINEAR,
    #         borderMode=cv2.BORDER_CONSTANT,
    #         borderValue=(255, 255, 255),
    #     )
    #     alt_overlay = create_overlay(reference_image, alt_aligned_image)
    #     cv2.imwrite(str(output_dir / "overlay_alt.png"), alt_overlay)
    #     logger.info(f"Saved: overlay_alt.png (alternative method for comparison)")

    result.fully_aligned = True
    session.commit()
    return FileStatus.WARNING
