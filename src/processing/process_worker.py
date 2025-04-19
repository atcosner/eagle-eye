import cv2
import logging
import numpy as np
from pathlib import Path

import requests
from sqlalchemy.orm import Session

from PyQt6.QtCore import QObject, pyqtSlot, pyqtSignal, QMutex, QMutexLocker

import src.util.processing as process_util
from src.database import DB_ENGINE
from src.database.input_file import InputFile
from src.database.job import Job
from src.database.fields.text_field import TextField
from src.database.page_region import PageRegion
from src.database.processed_fields.processed_text_field import ProcessedTextField
from src.util.google_api import open_api_session, ocr_text_region
from src.util.logging import NamedLoggerAdapter
from src.util.paths import LocalPaths
from src.util.status import FileStatus

logger = logging.getLogger(__name__)


class ProcessWorker(QObject):
    updateStatus = pyqtSignal(int, FileStatus)
    processComplete = pyqtSignal(int)

    def __init__(self, name: str, job_id: int, input_file_id: int, mutex: QMutex):
        super().__init__()
        self.mutex = mutex
        self._job_id = job_id
        self._input_file_id = input_file_id

        self.log = NamedLoggerAdapter(logger, f'Thread: {name}')

    def process_text_field(
            self,
            session: requests.Session,
            page_region: PageRegion,
            field: TextField,
            aligned_image: np.ndarray,
            roi_dest_path: Path,
    ) -> ProcessedTextField:
        # Snip and save off the ROI image
        process_util.snip_roi_image(aligned_image, field.visual_region, save_path=roi_dest_path)

        # Determine the region to OCR
        ocr_region = field.text_region if field.text_region is not None else field.visual_region

        from_controlled_language = False
        if field.checkbox_region is not None and process_util.get_checked(aligned_image, field.checkbox_region):
            assert field.checkbox_text is not None
            self.log.info(f'Detected checked default option, using: {field.checkbox_text}')
            ocr_result = field.checkbox_text
            from_controlled_language = True
        elif process_util.should_ocr_region(aligned_image, ocr_region):
            ocr_result = ocr_text_region(session, aligned_image, ocr_region, add_border=True)
        else:
            self.log.info(f'Detected mostly white image, skipping OCR')
            ocr_result = ''

        # TODO: Copy from previous region

        return ProcessedTextField(
            name=field.name,
            page_region=page_region.name,
            roi_path=roi_dest_path,
            ocr_result=ocr_result,
            allow_linking=False,
            copied_from_linked=False,
            from_controlled_language=from_controlled_language,
        )

    @pyqtSlot()
    def start(self) -> None:
        locker = QMutexLocker(self.mutex)
        self.log.info('Staring thread')

        with Session(DB_ENGINE) as session:
            job = session.get(Job, self._job_id)
            input_file = session.get(InputFile, self._input_file_id)

            assert input_file.pre_process_result.aligned_image_path.exists(), \
                f'Path does not exist: {input_file.pre_process_result.aligned_image_path}'

            # Load the aligned image from our pre-processing
            aligned_image = cv2.imread(
                str(input_file.pre_process_result.aligned_image_path),
                flags=cv2.IMREAD_GRAYSCALE,
            )

            # Create a working directory to store our ROI snips
            processing_directory = LocalPaths.processing_directory(job.uuid, input_file.id)
            processing_directory.mkdir()

            # Establish a session to the Google API
            api_session = open_api_session()

            # Work through all regions in the reference form
            for page_region in job.reference_form.regions:
                self.log.info(f'Processing region: "{page_region.name}"')
                for field in page_region.fields:
                    roi_path = processing_directory / f'{field.id}.png'

                    if field.text_field is not None:
                        self.log.info(f'Processing Text Field: {field.text_field.name}')
                        result_field = self.process_text_field(
                            session=api_session,
                            page_region=page_region,
                            field=field.text_field,
                            aligned_image=aligned_image,
                            roi_dest_path=roi_path,
                        )
