import cv2
import logging
import numpy as np
import requests
import shutil
from pathlib import Path
from sqlalchemy.orm import Session

from PyQt6.QtCore import QObject, pyqtSlot, pyqtSignal, QMutex, QMutexLocker

import src.util.processing as process_util
from src.database import DB_ENGINE
from src.database.fields.checkbox_field import CheckboxField
from src.database.fields.multi_checkbox_field import MultiCheckboxField
from src.database.fields.multiline_text_field import MultilineTextField
from src.database.fields.text_field import TextField
from src.database.input_file import InputFile
from src.database.job import Job
from src.database.process_result import ProcessResult
from src.database.processed_fields.processed_checkbox_field import ProcessedCheckboxField
from src.database.processed_fields.processed_field import ProcessedField
from src.database.processed_fields.processed_multi_checkbox_field import ProcessedMultiCheckboxField
from src.database.processed_fields.processed_multi_checkbox_option import ProcessedMultiCheckboxOption
from src.database.processed_fields.processed_multiline_text_field import ProcessedMultilineTextField
from src.database.processed_fields.processed_text_field import ProcessedTextField
from src.database.processed_region import ProcessedRegion
from src.util.google_api import open_api_session, ocr_text_region
from src.util.logging import NamedLoggerAdapter
from src.util.paths import LocalPaths
from src.util.status import FileStatus
from src.util.types import FormLinkingMethod
from src.util.validation import MultiCheckboxValidation

from . import validation

logger = logging.getLogger(__name__)


class ProcessWorker(QObject):
    updateStatus = pyqtSignal(int, FileStatus)
    processingComplete = pyqtSignal(int)

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
            linking_method: FormLinkingMethod,
            identifier_field: ProcessedTextField | None = None,
    ) -> tuple[bool, ProcessedTextField]:
        # Snip and save off the ROI image
        process_util.snip_roi_image(aligned_image, field.visual_region, save_path=roi_dest_path)

        # Determine the region to OCR
        ocr_region = field.text_region if field.text_region is not None else field.visual_region

        ocr_error = False
        from_controlled_language = False if field.checkbox_region is not None else None
        if field.checkbox_region is not None and process_util.get_checked(aligned_image, field.checkbox_region):
            assert field.checkbox_text is not None
            self.log.info(f'Detected checked default option, using: {field.checkbox_text}')
            ocr_result = field.checkbox_text
            from_controlled_language = True
        elif process_util.should_ocr_region(aligned_image, ocr_region):
            ocr_result = ocr_text_region(session, aligned_image, ocr_region, add_border=True)
            ocr_error = ocr_result is None
            self.log.info(f'OCR returned: "{ocr_result}"')
        else:
            self.log.info(f'Detected mostly white image, skipping OCR')
            ocr_result = ''

        # OCR result should not be None even if we had an error
        ocr_result = '' if ocr_error else ocr_result

        # Check if we should search for a linking field
        copied_from_linked = False if field.allow_copy else None
        if field.allow_copy and process_util.should_copy_from_previous(ocr_result):
            link_field = process_util.locate_linked_field(
                link_method=linking_method,
                current_field=field,
                identifier_field=identifier_field,
            )
            if link_field is None:
                self.log.warning(f'Failed to locate a field to link to')
            else:
                self.log.info(f'Located linked field: {link_field.name} -> "{link_field.text}"')
                copied_from_linked = True
                ocr_result = link_field.text

        field = ProcessedTextField(
            name=field.name,
            roi_path=roi_dest_path,
            text=ocr_result,
            ocr_text=ocr_result,
            copied_from_linked=copied_from_linked,
            from_controlled_language=from_controlled_language,
            text_field=field,
        )
        return ocr_error, field

    def process_multiline_text_field(
            self,
            session: requests.Session,
            field: MultilineTextField,
            aligned_image: np.ndarray,
            roi_dest_path: Path,
    ) -> tuple[bool, ProcessedMultilineTextField]:
        # Snip and save off the ROI image
        process_util.snip_roi_image(aligned_image, field.visual_region, save_path=roi_dest_path)

        # Multiline images need to be stitched together for OCR
        stitched_image = process_util.stitch_images(aligned_image, field.line_regions)

        # Check if any of our regions need to be OCR'd
        ocr_checks = [process_util.should_ocr_region(aligned_image, region) for region in field.line_regions]

        ocr_error = False
        if any(ocr_checks):
            ocr_result = ocr_text_region(session, roi=stitched_image, add_border=True)
            ocr_error = ocr_result is None
            self.log.info(f'OCR returned: "{ocr_result}"')
        else:
            self.log.info(f'Detected mostly white image, skipping OCR')
            ocr_result = ''

        # OCR result should not be None even if we had an error
        ocr_result = '' if ocr_error else ocr_result

        field = ProcessedMultilineTextField(
            name=field.name,
            roi_path=roi_dest_path,
            text=ocr_result,
            ocr_text=ocr_result,
            copied_from_linked=None,
            from_controlled_language=None,
            multiline_text_field=field,
        )
        return ocr_error, field

    def process_checkbox_field(
            self,
            field: CheckboxField,
            aligned_image: np.ndarray,
            roi_dest_path: Path,
    ) -> tuple[bool, ProcessedCheckboxField]:
        process_util.snip_roi_image(aligned_image, field.visual_region, save_path=roi_dest_path)

        checked = process_util.get_checked(aligned_image, field.checkbox_region)
        field = ProcessedCheckboxField(
            name=field.name,
            roi_path=roi_dest_path,
            checked=checked,
            checkbox_field=field,
        )
        return False, field

    def process_multi_checkbox_field(
            self,
            session: requests.Session,
            field: MultiCheckboxField,
            aligned_image: np.ndarray,
            roi_dest_path: Path,
    ) -> tuple[bool, ProcessedMultiCheckboxField]:
        # Snip and save off the ROI image
        process_util.snip_roi_image(aligned_image, field.visual_region, save_path=roi_dest_path)

        ocr_error = False
        checkboxes: dict[str, ProcessedMultiCheckboxOption] = {}
        for checkbox in field.checkboxes:
            checked = process_util.get_checked(aligned_image, checkbox.region)
            self.log.info(f'Checkbox "{checkbox.name}" = {checked}')

            # If the checkbox has a text region, check if we should run OCR
            optional_text: str | None = None
            if checkbox.text_region is not None:
                if process_util.should_ocr_region(aligned_image, checkbox.text_region):
                    optional_text = ocr_text_region(session, aligned_image, checkbox.text_region, add_border=True)
                    ocr_error = optional_text is None
                    self.log.info(f'OCR returned: "{optional_text}"')

                    # TODO: What if we did an OCR, but the checkbox was not checked?
                else:
                    self.log.info(f'Detected mostly white image, skipping OCR')
                    optional_text = ''

            checkboxes[checkbox.name] = ProcessedMultiCheckboxOption(
                name=checkbox.name,
                checked=checked,
                text=optional_text,
                ocr_text=optional_text,
                multi_checkbox_option=checkbox,
            )

        # Validate the field
        validation_result = validation.validate_multi_checkbox_field(field, checkboxes)

        field = ProcessedMultiCheckboxField(
            name=field.name,
            roi_path=roi_dest_path,
            validation_result=validation_result,
            multi_checkbox_field=field,
            checkboxes=checkboxes,
        )
        return ocr_error, field

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
            if processing_directory.exists():
                self.log.warning(f'Processing directory already exists: {processing_directory}')
                shutil.rmtree(processing_directory)
            processing_directory.mkdir()

            # Establish a session to the Google API
            api_session = open_api_session()

            result = ProcessResult()
            input_file.process_result = result

            # Work through all regions in the reference form
            processing_error = False
            identifier_field: ProcessedTextField | None = None
            for local_id, page_region in job.reference_form.regions.items():
                self.log.info('-' * 15)
                self.log.info(f'Processing region: "{page_region.name}" ({local_id})')
                processed_region = ProcessedRegion(local_id=page_region.local_id, name=page_region.name)

                # Sort the fields so that we process the identifier field first
                for field in sorted(page_region.fields, key=lambda f: f.identifier, reverse=True):
                    roi_path = processing_directory / f'{field.id}.png'
                    processed_field = ProcessedField(processing_error=False)

                    if field.text_field is not None:
                        self.log.info(f'Processing Text Field: {field.text_field.name}')
                        had_error, result_field = self.process_text_field(
                            session=api_session,
                            field=field.text_field,
                            aligned_image=aligned_image,
                            roi_dest_path=roi_path,
                            linking_method=job.reference_form.linking_method,
                            identifier_field=identifier_field,
                        )

                        # Save off the identifier field for later linking use
                        if field.identifier:
                            identifier_field = result_field

                        processed_field.processing_error = had_error
                        processed_field.text_field = result_field
                    elif field.multiline_text_field is not None:
                        self.log.info(f'Processing Multiline Text Field: {field.multiline_text_field.name}')
                        had_error, result_field = self.process_multiline_text_field(
                            session=api_session,
                            field=field.multiline_text_field,
                            aligned_image=aligned_image,
                            roi_dest_path=roi_path,
                        )

                        processed_field.processing_error = had_error
                        processed_field.multiline_text_field = result_field
                    elif field.checkbox_field is not None:
                        self.log.info(f'Processing Checkbox Field: {field.checkbox_field.name}')
                        had_error, result_field = self.process_checkbox_field(
                            field=field.checkbox_field,
                            aligned_image=aligned_image,
                            roi_dest_path=roi_path,
                        )

                        processed_field.processing_error = had_error
                        processed_field.checkbox_field = result_field
                    elif field.multi_checkbox_field is not None:
                        self.log.info(f'Processing Multi-Checkbox Field: {field.multi_checkbox_field.name}')
                        had_error, result_field = self.process_multi_checkbox_field(
                            session=api_session,
                            field=field.multi_checkbox_field,
                            aligned_image=aligned_image,
                            roi_dest_path=roi_path,
                        )

                        processed_field.processing_error = had_error
                        processed_field.multi_checkbox_field = result_field
                    else:
                        self.log.error(f'Form field had no parts to process')
                        processed_field.processing_error = True

                    # Add the processed field to our region
                    processing_error = processed_field.processing_error
                    processed_region.fields.append(processed_field)

                # Add the processed region to the result
                result.regions[processed_region.local_id] = processed_region

            # Commit the results to the DB and signal out that our status is changed
            session.commit()
            self.updateStatus.emit(input_file.id, FileStatus.SUCCESS if not processing_error else FileStatus.FAILED)
            self.processingComplete.emit(input_file.id)
