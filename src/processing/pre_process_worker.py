import cv2
import logging
import numpy as np
import pymupdf
from sqlalchemy.orm import Session

from PyQt6.QtCore import QObject, pyqtSlot, pyqtSignal, QMutex, QMutexLocker

from src.database import DB_ENGINE
from src.database.input_file import InputFile
from src.database.job import Job
from src.database.pre_process_result import PreProcessResult
from src.util.logging import NamedLoggerAdapter
from src.util.paths import LocalPaths
from src.util.status import FileStatus
from src.util.types import FormAlignmentMethod

from .alignment import AlignmentError, AlignmentFailed, reference_mark_alignment, automatic_alignment

logger = logging.getLogger(__name__)


class PreProcessingWorker(QObject):
    updateStatus = pyqtSignal(int, FileStatus)
    processingComplete = pyqtSignal(int)

    def __init__(self, job_id: int, file_id: int, mutex: QMutex):
        super().__init__()
        self.mutex = mutex
        self.job_id = job_id
        self.file_id = file_id

        self.job: Job | None = None
        self.input_file: InputFile | None = None

        self.log = NamedLoggerAdapter(logger, f'Thread: {file_id}')

    def finish(self, session: Session, status: FileStatus) -> None:
        session.commit()
        self.updateStatus.emit(self.input_file.id, status)
        self.processingComplete.emit(self.input_file.id)

    def process(self) -> None:
        with Session(DB_ENGINE) as session:
            self.job = session.get(Job, self.job_id)
            self.input_file = session.get(InputFile, self.file_id)

            # do not pre-process container files
            if self.input_file.container_file:
                self.log.info('File is marked as a container file, skipping')
                self.processingComplete.emit(self.input_file.id)
                return

            # if we are linked, check if we need to save off our page from the PDF
            if self.input_file.linked_input_file_id is not None and not self.input_file.path.exists():
                linked_file = session.get(InputFile, self.input_file.linked_input_file_id)
                if linked_file is None:
                    self.log.error(f'Could not find the linked file with ID: {self.input_file.linked_input_file_id}')
                    self.updateStatus.emit(self.input_file.id, FileStatus.FAILED)
                    self.processingComplete.emit(self.input_file.id)
                    return

                self.log.error(f'Extracting page from linked file: {linked_file.path.name}')

                # TODO: could put the page number in the DB?
                page_number = int(str(self.input_file.path.stem).split('page')[-1])

                # extract the page from the PDF and save it to our path
                document = pymupdf.open(linked_file.path)
                page_pixmap = document.load_page(page_number-1).get_pixmap(dpi=300)
                page_pixmap.save(self.input_file.path)

            self.log.info(f'Using reference: {self.job.reference_form.name}')
            self.input_file.pre_process_result = PreProcessResult(successful_alignment=False, fully_aligned=False)

            # check that we have valid files
            if not self.input_file.path.exists():
                self.log.error(f'Test image did not exist: {self.input_file.path}')
                self.finish(session, FileStatus.FAILED)
                return

            if not self.job.reference_form.path.exists():
                self.log.error(f'Ref image did not exist: {self.job.reference_form.path}')
                self.finish(session, FileStatus.FAILED)
                return

            # Build the paths for our output results
            pre_process_directory = LocalPaths.pre_processing_directory(self.job.uuid, self.input_file.id)
            pre_process_directory.mkdir(exist_ok=True)

            # Load and grayscale both images
            input_image = cv2.imread(str(self.input_file.path))
            input_image_gray = cv2.cvtColor(input_image, cv2.COLOR_BGR2GRAY)
            _, input_image_threshold = cv2.threshold(input_image_gray, 127, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

            reference_image = cv2.imread(str(self.job.reference_form.path))
            reference_image_gray = cv2.cvtColor(reference_image, cv2.COLOR_BGR2GRAY)

            # Align the images based on the method in the reference form
            match self.job.reference_form.alignment_method:
                case FormAlignmentMethod.ALIGNMENT_MARKS:
                    self.log.info('Aligning images using alignment marks')

                    # rotate and attempt to align the images
                    try:
                        status = reference_mark_alignment(
                            logger=self.log,
                            session=session,
                            working_directory=pre_process_directory,
                            reference_image=reference_image_gray,
                            test_image=input_image_threshold,
                            alignment_mark_count=self.job.reference_form.alignment_mark_count,  # noqa
                            result=self.input_file.pre_process_result,  # noqa
                        )
                        self.finish(session, status)

                    except (AlignmentError, AlignmentFailed):
                        self.finish(session, FileStatus.FAILED)

                case FormAlignmentMethod.AUTOMATIC:
                    self.log.info('Aligning images using automatic alignment')

                    try:
                        status = automatic_alignment(
                            logger=self.log,
                            session=session,
                            working_directory=pre_process_directory,
                            reference_image=reference_image_gray,
                            test_image=input_image_threshold,
                            result=self.input_file.pre_process_result,  # noqa
                        )
                        self.finish(session, status)

                    except (AlignmentError, AlignmentFailed):
                        self.finish(session, FileStatus.FAILED)

                case _:
                    raise RuntimeError(f'Unknown alignment method: {self.job.reference_form.alignment_method}')

    @pyqtSlot()
    def start(self) -> None:
        locker = QMutexLocker(self.mutex)
        self.log.info('Staring thread')

        try:
            self.process()
        except Exception:
            # don't let unhandled exceptions cause issues with threads
            self.log.exception('Unhandled exception during pre-processing')
            self.updateStatus.emit(self.input_file.id, FileStatus.FAILED)
            self.processingComplete.emit(self.input_file.id)
