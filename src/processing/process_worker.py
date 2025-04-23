import cv2
import logging
import numpy as np
from pathlib import Path

import requests
from sqlalchemy.orm import Session

from PyQt6.QtCore import QObject, pyqtSlot, pyqtSignal, QMutex, QMutexLocker

import src.util.processing as process_util
from src.database import DB_ENGINE
from src.database.fields.text_field import TextField
from src.database.input_file import InputFile
from src.database.job import Job
from src.database.process_result import ProcessResult
from src.database.processed_fields.processed_field import ProcessedField
from src.database.processed_fields.processed_text_field import ProcessedTextField
from src.database.processed_region import ProcessedRegion
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
            self.log.info(f'OCR returned: "{ocr_result}"')
        else:
            self.log.info(f'Detected mostly white image, skipping OCR')
            ocr_result = ''

        # Check if we should search for a linking field
        copied_from_linked = False
        if field.allow_copy and process_util.should_copy_from_previous(ocr_result):
            link_field = process_util.locate_linked_field()
            if link_field is None:
                self.log.warning(f'Failed to locate a field to link to')
            else:
                self.log.info(f'Located linked field: {link_field.name} -> "{link_field.text}"')
                copied_from_linked = True
                ocr_result = link_field.text

        return ProcessedTextField(
            name=field.name,
            roi_path=roi_dest_path,
            ocr_result=ocr_result,
            text=ocr_result,
            copied_from_linked=copied_from_linked,
            from_controlled_language=from_controlled_language,
            text_field=field,
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

            result = ProcessResult()
            input_file.process_result = result

            # Work through all regions in the reference form
            for local_id, page_region in job.reference_form.regions.items():
                self.log.info(f'Processing region: "{page_region.name}" ({local_id})')
                processed_region = ProcessedRegion(local_id=page_region.local_id, name=page_region.name)

                # Sort the fields so that we process the identifier field first
                for field in sorted(page_region.fields, key=lambda f: f.identifier, reverse=True):
                    roi_path = processing_directory / f'{field.id}.png'
                    processed_field = ProcessedField()

                    if field.text_field is not None:
                        self.log.info(f'Processing Text Field: {field.text_field.name}')
                        result_field = self.process_text_field(
                            session=api_session,
                            field=field.text_field,
                            aligned_image=aligned_image,
                            roi_dest_path=roi_path,
                        )
                        processed_field.text_field = result_field
                    else:
                        self.log.error(f'Form field had no parts to process')
                        continue

                    # Add the processed field to our region
                    processed_region.fields.append(processed_field)

                # Add the processed region to the result
                result.regions[processed_region.local_id] = processed_region

            # Commit the results to the DB and signal out that our status is changed
            session.commit()
            self.updateStatus.emit(input_file.id, FileStatus.SUCCESS)
            self.processComplete.emit(input_file.id)
