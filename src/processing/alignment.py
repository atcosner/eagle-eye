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

# configuration for automatic alignment
MAX_FEATURES = 2000             # higher count so ORB finds structure throughout the full form,
                                 # not just in the dense header region
LOWE_RATIO = 0.75               # Lowe's ratio test threshold — discard a match when the
                                 # second-best candidate is within 75% of the best distance,
                                 # indicating the feature is ambiguous (common with handwriting)
MIN_INLIER_RATIO = 0.15         # RANSAC inliers as a fraction of good matches
                                 # (kept low because handwriting features on the test image
                                 # can never match the blank reference and are always outliers)
MIN_INLIER_Y_COVERAGE = 0.40    # inliers must span at least 40% of the image height;
                                 # a narrow band of inliers means the bottom is extrapolated
MIN_ALIGNMENT_NCC = 0.5         # minimum NCC — kept for reference but currently informational only
# Geometric sanity bounds — a flatbed scan of a flat document should only ever differ
# from the reference by a small rotation and near-unity scale; anything outside these
# ranges means RANSAC converged on a wrong solution.
MAX_ROTATION_DEGREES = 10.0     # reject transforms with |rotation| greater than this
MAX_SCALE_DEVIATION = 0.35      # reject transforms where scale differs from 1.0 by more than 35%


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


def _filter_matches_by_displacement(
        matches: list[cv2.DMatch],
        test_keypoints: list[cv2.KeyPoint],
        ref_keypoints: list[cv2.KeyPoint],
        image_height: int,
        image_width: int,
        tolerance_fraction: float = 0.04,
        seeded_median: np.ndarray | None = None,
) -> list[cv2.DMatch]:
    """Keep only matches whose (dx, dy) displacement is near the expected shift.

    When seeded_median is provided (e.g. from phase correlation), it is used as
    the centre of the filter window instead of computing the median from potentially
    garbage matches. This is critical: if most SIFT matches are wrong (displacements
    spanning the full image), the match-derived median is itself wrong, causing the
    filter to keep all garbage. A phase-correlation seed bypasses that entirely.

    No fallback: if fewer than 4 matches survive, the short list is returned and
    the caller is responsible for handling insufficient matches. The old fallback
    of returning the full unfiltered set was harmful — it passed garbage match sets
    to RANSAC, producing wildly wrong rotation/scale estimates.
    """
    if len(matches) < 2:
        return matches

    displacements = np.array([
        [
            ref_keypoints[m.trainIdx].pt[0] - test_keypoints[m.queryIdx].pt[0],
            ref_keypoints[m.trainIdx].pt[1] - test_keypoints[m.queryIdx].pt[1],
        ]
        for m in matches
    ], dtype=np.float64)

    center = seeded_median if seeded_median is not None else np.median(displacements, axis=0)
    tolerance = tolerance_fraction * max(image_height, image_width)
    distances = np.linalg.norm(displacements - center, axis=1)
    return [m for m, d in zip(matches, distances) if d < tolerance]



def _detect_features_grid(
        image: np.ndarray,
        total_features: int = MAX_FEATURES,
        rows: int = 8,
        cols: int = 4,
) -> tuple[list[cv2.KeyPoint], np.ndarray | None]:
    """Detect SIFT keypoints on the full image then spatially subsample per grid cell.

    No mask is used: detecting on the full image lets SIFT find printed form labels
    (section titles, field names, row numbers) which are unique per section and give
    much more distinctive descriptors than line-junction features from a structure mask.
    Handwriting features in the test image are naturally suppressed by cross-check
    matching — they have no counterpart in the blank reference, so they will never be
    mutual nearest neighbours.

    Rows are doubled (8×4) compared to the old 4×4 grid to improve vertical
    discrimination and reduce same-cell cross-row matching.

    detectAndCompute runs in one call so keypoints and descriptors share the same
    octave pyramid — no octave mismatch.
    """
    h, w = image.shape[:2]
    sift = cv2.SIFT_create(nfeatures=total_features)  # type: ignore[attr-defined]
    keypoints, descriptors = sift.detectAndCompute(image, None)

    if descriptors is None or not keypoints:
        return [], None

    # Redistribute: for each grid cell keep only the top-response keypoints so that
    # the lower half of the form (which has fewer high-contrast features than the
    # dense header) still gets representation in the final feature set.
    features_per_cell = max(10, total_features // (rows * cols))
    selected: list[int] = []

    for r in range(rows):
        for c in range(cols):
            y1, y2 = r * h // rows, (r + 1) * h // rows
            x1, x2 = c * w // cols, (c + 1) * w // cols
            cell_indices = [
                i for i, kp in enumerate(keypoints)
                if x1 <= kp.pt[0] < x2 and y1 <= kp.pt[1] < y2
            ]
            cell_indices.sort(key=lambda i: keypoints[i].response, reverse=True)
            selected.extend(cell_indices[:features_per_cell])

    if not selected:
        return [], None

    return [keypoints[i] for i in selected], descriptors[selected]


def _extract_structure_mask(image: np.ndarray) -> np.ndarray:
    """Return a float64 binary mask containing only long form lines.

    Morphological opening with long 1-D kernels keeps only strokes that span
    at least 20 % of the image width (horizontal) or 10 % of the image height
    (vertical).  Handwriting strokes are much shorter and are removed entirely.
    The result is a sparse mask of form structure that is identical (modulo
    translation) in the blank reference and any filled-in scan.
    """
    h, w = image.shape[:2]
    _, binary = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    # Long horizontal lines (table borders, header box)
    min_h_len = max(30, int(0.20 * w))
    k_h = cv2.getStructuringElement(cv2.MORPH_RECT, (min_h_len, 1))
    long_h = cv2.morphologyEx(binary, cv2.MORPH_OPEN, k_h)

    # Long vertical lines (column separators, outer border)
    min_v_len = max(30, int(0.10 * h))
    k_v = cv2.getStructuringElement(cv2.MORPH_RECT, (1, min_v_len))
    long_v = cv2.morphologyEx(binary, cv2.MORPH_OPEN, k_v)

    structure = cv2.bitwise_or(long_h, long_v)
    return structure.astype(np.float64)


def _estimate_translation_by_structure(
        reference_image: np.ndarray,
        test_image: np.ndarray,
) -> tuple[np.ndarray, float]:
    """Estimate translation by phase-correlating form structure line masks.

    Full-image phase correlation fails because per-page handwriting shifts the
    dominant cross-correlation peak.  By first extracting only long form lines
    (removing handwriting with morphological opening) the correlation is driven
    purely by the stable printed structure, which is identical in every scan.

    Returns:
        displacement – np.array([dx, dy]) where dx = ref_x − test_x, matching
                       the sign convention used by _filter_matches_by_displacement
        confidence   – phaseCorrelate response value (dimensionless; the same
                       image pair gives ~10–50× higher response on structure masks
                       than on raw pixel values)
    """
    ref_h, ref_w = reference_image.shape[:2]
    test_h, test_w = test_image.shape[:2]

    ref_structure = _extract_structure_mask(reference_image)
    test_structure = _extract_structure_mask(test_image)

    if (ref_h, ref_w) == (test_h, test_w):
        ref_pad = ref_structure
        test_pad = test_structure
    else:
        max_h, max_w = max(ref_h, test_h), max(ref_w, test_w)
        ref_pad = np.zeros((max_h, max_w), dtype=np.float64)
        ref_pad[:ref_h, :ref_w] = ref_structure
        test_pad = np.zeros((max_h, max_w), dtype=np.float64)
        test_pad[:test_h, :test_w] = test_structure

    # phaseCorrelate(ref, test) returns shift such that test ≈ shift(ref, shift)
    # → displacement = ref_pt − test_pt = −shift
    shift, response = cv2.phaseCorrelate(ref_pad, test_pad)
    displacement = np.array([-shift[0], -shift[1]], dtype=np.float64)
    return displacement, float(response)


# Minimum structure-mask phaseCorrelate response to trust the estimator.
# The blank reference has clean, high-contrast lines; even a lightly inked scan
# should produce a response well above this when the structure masks align.
STRUCTURE_MIN_RESPONSE = 0.05


def automatic_alignment(
        logger: logging.Logger | NamedLoggerAdapter,
        session: Session,
        working_directory: Path,
        reference_image: np.ndarray,
        test_image: np.ndarray,
        result: PreProcessResult,
) -> FileStatus:
    matches_path, aligned_path, overlaid_path = build_image_paths(working_directory)

    # ── Step 1: coarse translation estimate ──────────────────────────────────
    # Phase-correlate structure masks (long form lines only, handwriting removed)
    # rather than raw pixels.  Handwriting shifts the dominant peak in full-image
    # phase correlation; the structure masks eliminate that noise source entirely.
    struct_displacement, struct_response = _estimate_translation_by_structure(
        reference_image, test_image
    )
    logger.info(
        f'Structure phase correlation: displacement=({struct_displacement[0]:.1f}, '
        f'{struct_displacement[1]:.1f}), response={struct_response:.4f}'
    )

    if struct_response >= STRUCTURE_MIN_RESPONSE:
        translation_seed = struct_displacement
        translation_source = f'structure (response={struct_response:.4f})'
    else:
        # Fall back to raw-pixel phase correlation when the structure mask is too
        # sparse (e.g. very lightly printed form or extreme scan brightness).
        ref_h, ref_w = reference_image.shape[:2]
        test_h, test_w = test_image.shape[:2]
        if (ref_h, ref_w) == (test_h, test_w):
            pc_src_ref = reference_image.astype(np.float64)
            pc_src_test = test_image.astype(np.float64)
        else:
            max_h, max_w = max(ref_h, test_h), max(ref_w, test_w)
            pc_src_ref = np.zeros((max_h, max_w), dtype=np.float64)
            pc_src_ref[:ref_h, :ref_w] = reference_image.astype(np.float64)
            pc_src_test = np.zeros((max_h, max_w), dtype=np.float64)
            pc_src_test[:test_h, :test_w] = test_image.astype(np.float64)
        pc_shift, pc_response = cv2.phaseCorrelate(pc_src_ref, pc_src_test)
        translation_seed = np.array([-pc_shift[0], -pc_shift[1]])
        translation_source = f'raw phase correlation (response={pc_response:.4f})'
        logger.warning(
            f'Structure response {struct_response:.4f} below threshold '
            f'{STRUCTURE_MIN_RESPONSE} — falling back to raw phase correlation: '
            f'shift=({pc_shift[0]:.1f}, {pc_shift[1]:.1f}), response={pc_response:.4f}'
        )

    logger.info(
        f'Translation seed ({translation_source}): '
        f'({translation_seed[0]:.1f}, {translation_seed[1]:.1f})'
    )

    ref_keypoints, ref_descriptors = _detect_features_grid(reference_image)
    test_keypoints, test_descriptors = _detect_features_grid(test_image)
    logger.info(f'Found {len(ref_keypoints)} reference keypoints and {len(test_keypoints)} test keypoints')

    if ref_descriptors is None or test_descriptors is None:
        logger.error('Failed to detect any features in one or both images — cannot align')
        result.alignment_possible = False
        result.fully_aligned = False
        session.commit()
        return FileStatus.FAILED

    # Match with Lowe's ratio test AND cross-check (mutual nearest neighbour).
    # Cross-check requires test→ref and ref→test to agree on the same pairing.
    # For repetitive form structure (many nearly-identical row junctions) this is a much
    # stronger correctness signal than ratio-test alone: a cross-row false match is only
    # accepted if the reference feature also considers that test feature its best match,
    # which is very unlikely when every row has a visually similar counterpart.
    matcher = cv2.BFMatcher(cv2.NORM_L2)
    knn_fwd = matcher.knnMatch(test_descriptors, ref_descriptors, k=2)
    knn_bwd = matcher.knnMatch(ref_descriptors, test_descriptors, k=1)

    # Build reverse lookup: ref_feature_index → index of its nearest test feature
    best_test_for_ref: dict[int, int] = {
        pair[0].queryIdx: pair[0].trainIdx for pair in knn_bwd if pair
    }

    # Keep forward matches that pass Lowe's ratio AND are mutually consistent
    matches: list[cv2.DMatch] = [
        m for pair in knn_fwd
        if len(pair) == 2
        for m, n in [pair]
        if m.distance < LOWE_RATIO * n.distance
        and best_test_for_ref.get(m.trainIdx) == m.queryIdx
    ]
    logger.info(
        f'Found {len(matches)} matches after Lowe ratio test + cross-check '
        f'(threshold: {LOWE_RATIO})'
    )

    # Displacement filter seeded from the translation estimate.
    # Only matches whose (ref − test) displacement is within 4% of the image's larger
    # dimension from the seed are kept.  Using a pre-computed seed means the filter
    # centre is always the correct translation rather than the median of potentially
    # garbage SIFT matches.
    matches = _filter_matches_by_displacement(
        matches, test_keypoints, ref_keypoints,
        test_image.shape[0], test_image.shape[1],
        seeded_median=translation_seed,
    )
    logger.info(f'{len(matches)} matches after displacement filter (seeded from {translation_source})')

    # Save the matches image — informational even when few matches survive
    matched_image = cv2.drawMatches(
        test_image, test_keypoints,
        reference_image, ref_keypoints,
        matches, None,  # type: ignore[arg-type]
    )
    logger.info(f'Writing matches image: {matches_path}')
    cv2.imwrite(str(matches_path), matched_image)
    result.matches_image_path = matches_path

    result.alignment_possible = False
    result.fully_aligned = False
    alignment_failed = False

    if len(matches) < 4:
        # Not enough SIFT matches survived for RANSAC — use the coarse translation
        # seed directly as a pure-translation affine matrix.
        # translation_seed = [dx, dy] = ref_pt − test_pt, so the affine matrix that
        # maps each test point to ref space is [[1,0,dx],[0,1,dy]].
        logger.warning(
            f'Only {len(matches)} SIFT match(es) survived — falling back to '
            f'{translation_source} pure translation '
            f'({translation_seed[0]:.1f}, {translation_seed[1]:.1f})'
        )
        matrix_aff = np.array([
            [1.0, 0.0, translation_seed[0]],
            [0.0, 1.0, translation_seed[1]],
        ], dtype=np.float64)
        result.alignment_possible = True
        alignment_failed = True  # WARNING: no RANSAC geometric verification
    else:
        # RANSAC path — enough SIFT matches to estimate a full similarity transform.
        test_points = np.zeros((len(matches), 2), dtype="float")
        ref_points = np.zeros((len(matches), 2), dtype="float")
        for (idx, match) in enumerate(matches):
            test_points[idx] = test_keypoints[match.queryIdx].pt
            ref_points[idx] = ref_keypoints[match.trainIdx].pt

        # Estimate a similarity transform (translation + rotation + uniform scale, 4 DOF).
        (matrix_aff, ransac_mask) = cv2.estimateAffinePartial2D(test_points, ref_points, method=cv2.RANSAC)

        if matrix_aff is None:
            logger.error('estimateAffinePartial2D failed to compute a valid similarity matrix')
            session.commit()
            return FileStatus.FAILED

        # Geometric sanity: decompose and reject physically impossible transforms.
        scale = float(np.sqrt(matrix_aff[0, 0] ** 2 + matrix_aff[1, 0] ** 2))
        angle_deg = float(np.degrees(np.arctan2(matrix_aff[1, 0], matrix_aff[0, 0])))
        logger.info(f'Estimated transform: rotation={angle_deg:.2f}°, scale={scale:.4f}')
        if abs(angle_deg) > MAX_ROTATION_DEGREES:
            logger.error(
                f'Estimated rotation {angle_deg:.2f}° exceeds maximum allowed '
                f'({MAX_ROTATION_DEGREES}°) — RANSAC converged on a wrong solution'
            )
            session.commit()
            return FileStatus.FAILED
        if abs(scale - 1.0) > MAX_SCALE_DEVIATION:
            logger.error(
                f'Estimated scale {scale:.4f} deviates from 1.0 by more than '
                f'{MAX_SCALE_DEVIATION:.0%} — RANSAC converged on a wrong solution'
            )
            session.commit()
            return FileStatus.FAILED

        result.alignment_possible = True

        inlier_count = int(ransac_mask.sum())
        inlier_ratio = inlier_count / len(matches)
        logger.info(f'RANSAC inliers: {inlier_count}/{len(matches)} ({inlier_ratio:.2%})')
        if inlier_ratio < MIN_INLIER_RATIO:
            logger.error(
                f'RANSAC inlier ratio {inlier_ratio:.2%} is below the minimum threshold '
                f'({MIN_INLIER_RATIO:.2%}) — alignment is unreliable'
            )
            alignment_failed = True

        inlier_pts = test_points[ransac_mask.ravel() == 1]
        y_coverage = (inlier_pts[:, 1].max() - inlier_pts[:, 1].min()) / test_image.shape[0]
        logger.info(f'Inlier vertical coverage: {y_coverage:.2%} (threshold: {MIN_INLIER_Y_COVERAGE:.2%})')
        if y_coverage < MIN_INLIER_Y_COVERAGE:
            logger.error(
                f'Inliers only cover {y_coverage:.2%} of image height — '
                f'alignment below the matched region is unreliable'
            )
            alignment_failed = True

    # Warp and save — common to both the RANSAC and phase-correlation paths
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

    result.fully_aligned = not alignment_failed
    session.commit()
    return FileStatus.WARNING if alignment_failed else FileStatus.SUCCESS
