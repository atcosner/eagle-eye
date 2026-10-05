import cv2
import logging
from sqlalchemy.orm import Session

from PyQt6.QtCore import QObject, pyqtSlot, pyqtSignal, QMutex, QMutexLocker

from src.database import DB_ENGINE
from src.database.input_file import InputFile
from src.database.job import Job
from src.util.logging import NamedLoggerAdapter
from src.util.paths import LocalPaths
from src.util.status import FileStatus

from .alignment import AlignmentError, AlignmentFailed, refine_alignment

logger = logging.getLogger(__name__)


class AlignmentRefineWorker(QObject):
    updateStatus = pyqtSignal(int, FileStatus)
    refinementFailed = pyqtSignal(int)
    processingComplete = pyqtSignal(int)

    def __init__(self, job_id: int, file_id: int, mutex: QMutex):
        super().__init__()
        self.mutex = mutex
        self.job_id = job_id
        self.file_id = file_id

        self.log = NamedLoggerAdapter(logger, f'Thread: {file_id}')

    def process(self) -> bool:
        with Session(DB_ENGINE) as session:
            job = session.get(Job, self.job_id)
            input_file = session.get(InputFile, self.file_id)

            result = input_file.pre_process_result
            if result is None or not result.alignment_possible or result.aligned_image_path is None:
                self.log.error('File does not have an aligned image to refine')
                return False

            # The alignment needs to be confirmed again after a re-run, even if it fails
            result.alignment_confirmed = False
            session.commit()

            if not job.reference_form.path.exists():
                self.log.error(f'Ref image did not exist: {job.reference_form.path}')
                return False

            reference_image = cv2.imread(str(job.reference_form.path))
            reference_image_gray = cv2.cvtColor(reference_image, cv2.COLOR_BGR2GRAY)

            self.log.info('Refining the alignment of the aligned image')
            try:
                refine_alignment(
                    logger=self.log,
                    session=session,
                    working_directory=LocalPaths.pre_processing_directory(job.uuid, input_file.id),
                    reference_image=reference_image_gray,
                    result=result,
                )
            except (AlignmentError, AlignmentFailed):
                self.log.error('Failed to refine the alignment, keeping the previous alignment')
                return False

        return True

    @pyqtSlot()
    def start(self) -> None:
        locker = QMutexLocker(self.mutex)
        self.log.info('Staring thread')

        try:
            success = self.process()
        except Exception:
            # don't let unhandled exceptions cause issues with threads
            self.log.exception('Unhandled exception during alignment refinement')
            success = False

        if not success:
            self.refinementFailed.emit(self.file_id)

        # The file needs to be confirmed again either way
        self.updateStatus.emit(self.file_id, FileStatus.PENDING)
        self.processingComplete.emit(self.file_id)
