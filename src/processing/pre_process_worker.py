import cv2
import logging
from sqlalchemy.orm import Session

from PyQt6.QtCore import QObject, pyqtSlot, pyqtSignal, QMutex, QMutexLocker

from src.database import DB_ENGINE
from src.database.input_file import InputFile
from src.database.job import Job
from src.database.pre_process_result import PreProcessResult
from src.database.rotation_attempt import RotationAttempt
from src.util.logging import NamedLoggerAdapter
from src.util.status import FileStatus
from src.util.types import InputFileDetails

from .util import rotate_image, find_alignment_marks, AlignmentMark, alignment_marks_to_points

logger = logging.getLogger(__name__)

# TODO: Control this with a user setting
# Allow for an image to be +/- 6 degrees rotated
ALLOWED_ROTATIONS = [0] + list(range(1, 6, 1)) + list(range(-1, -6, -1))


class PreProcessingWorker(QObject):
    updateStatus = pyqtSignal(int, FileStatus)
    processingComplete = pyqtSignal(int)

    def __init__(self, job_id: int, file_details: InputFileDetails, mutex: QMutex):
        super().__init__()
        self.mutex = mutex
        self.job_id = job_id
        self.file_details = file_details

        self.log = NamedLoggerAdapter(logger, {'name': f'Thread: {file_details.path.name}'})

    @pyqtSlot()
    def start(self) -> None:
        locker = QMutexLocker(self.mutex)
        self.log.info('Staring thread')

        with Session(DB_ENGINE) as session:
            job = session.get(Job, self.job_id)
            input_file = session.get(InputFile, self.file_details.db_id)

            assert self.file_details.path.exists(), f'Test image did not exist: {self.file_details.path}'
            assert job.reference_form.path.exists(), f'Ref image did not exist: {job.reference_form.path}'

            self.log.info(f'Using reference: {job.reference_form.name}')
            input_file.pre_process_result = PreProcessResult(successful_match=False)

            # Build the paths for our output results
            matches_path = self.file_details.path.parent / 'matches.png'
            aligned_path = self.file_details.path.parent / 'aligned.png'
            overlaid_path = self.file_details.path.parent / 'overlaid.png'

            # Load and grayscale both images
            input_image = cv2.imread(str(input_file.path))
            input_image_gray = cv2.cvtColor(input_image, cv2.COLOR_BGR2GRAY)
            _, input_image_threshold = cv2.threshold(input_image_gray, 127, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

            reference_image = cv2.imread(str(job.reference_form.path))
            reference_image_gray = cv2.cvtColor(reference_image, cv2.COLOR_BGR2GRAY)

            # Find the alignment marks in the reference image
            reference_alignment_marks = find_alignment_marks(reference_image_gray)
            self.log.info(
                f'Reference Image: Found {len(reference_alignment_marks)} marks, \
                expected {job.reference_form.alignment_mark_count}'
            )
            assert len(reference_alignment_marks) == job.reference_form.alignment_mark_count

            # Work through each rotation angle and check for alignment marks
            detected_marks: dict[int, list[AlignmentMark]] = {}
            for rotation_angle in ALLOWED_ROTATIONS:
                # Rotate the image
                rotated_image = input_image_threshold
                if rotation_angle != 0:
                    rotated_image = rotate_image(rotated_image, rotation_angle)

                rotated_path = self.file_details.path.parent / f'rotation_{rotation_angle}.png'
                cv2.imwrite(str(rotated_path), rotated_image)

                alignment_marks = find_alignment_marks(rotated_image)
                self.log.info(f'Rotation Result: {rotation_angle} degrees, {len(alignment_marks)} alignment marks')
                detected_marks[rotation_angle] = alignment_marks

                # Save the attempt in the DB
                input_file.pre_process_result.rotation_attempts[rotation_angle] = RotationAttempt(
                    rotation_angle=rotation_angle,
                    path=rotated_path,
                )

            session.commit()

            # Chose the best rotation that found all the alignment marks
            best_angle: int | None = None
            for angle, marks in detected_marks.items():
                if len(marks) == job.reference_form.alignment_mark_count:
                    best_angle = angle
                    break

            self.log.info(f'Best rotation angle: {best_angle} degrees')
            if best_angle is None:
                self.updateStatus.emit(input_file.id, FileStatus.FAILED)
                return
            input_file.pre_process_result.successful_match = True
            input_file.pre_process_result.accepted_rotation_angle = best_angle

            # Convert the alignment marks to matchpoints
            input_matchpoints = alignment_marks_to_points(detected_marks[best_angle])
            ref_matchpoints = alignment_marks_to_points(reference_alignment_marks)

            # Save an image of the matches
            input_image_rotated = rotate_image(input_image_threshold, best_angle)
            matched_image = cv2.drawMatches(
                input_image_rotated,
                [cv2.KeyPoint(x, y, 2) for x, y in input_matchpoints],
                reference_image,
                [cv2.KeyPoint(x, y, 2) for x, y in ref_matchpoints],
                [cv2.DMatch(x, x, 1) for x in range(len(ref_matchpoints))],
                None,
            )
            self.log.info(f'Writing matches image: {matches_path}')
            cv2.imwrite(str(matches_path), matched_image)
            input_file.pre_process_result.matches_image_path = matches_path

            # Compute the homography matrix and align the images using it
            (matrix_h, _) = cv2.findHomography(input_matchpoints, ref_matchpoints, method=cv2.RANSAC)
            (h, w) = reference_image.shape[:2]
            aligned_image = cv2.warpPerspective(input_image_rotated, matrix_h, (w, h))
            self.log.info(f'Writing aligned image: {aligned_path}')
            cv2.imwrite(str(aligned_path), aligned_image)

            # Save an overlaid image to assist in debugging
            overlaid_image = aligned_image.copy()
            cv2.addWeighted(reference_image_gray, 0.5, aligned_image, 0.5, 0, overlaid_image)
            self.log.info(f'Writing overlaid image: {overlaid_path}')
            cv2.imwrite(str(overlaid_path), overlaid_image)

            session.commit()
            self.updateStatus.emit(input_file.id, FileStatus.SUCCESS)
            self.processingComplete.emit(input_file.id)
