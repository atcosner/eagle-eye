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
from src.database.fields.circled_field import CircledField
from src.database.fields.checkbox_field import CheckboxField
from src.database.fields.multi_checkbox_field import MultiCheckboxField
from src.database.fields.text_field import TextField
from src.database.input_file import InputFile
from src.database.job import Job
from src.database.processed_fields.processed_circled_field import ProcessedCircledField
from src.database.processed_fields.processed_circled_option import ProcessedCircledOption
from src.database.processed_fields.processed_checkbox_field import ProcessedCheckboxField
from src.database.processed_fields.processed_field import ProcessedField
from src.database.processed_fields.processed_field_group import ProcessedFieldGroup
from src.database.processed_fields.processed_multi_checkbox_field import ProcessedMultiCheckboxField
from src.database.processed_fields.processed_multi_checkbox_option import ProcessedMultiCheckboxOption
from src.database.processed_fields.processed_text_field import ProcessedTextField
from src.database.processing.processed_region import ProcessedRegion
from src.database.processing.process_result import ProcessResult
from src.database.validation.validation_result import ValidationResult
from src.util.google_api import open_api_session, ocr_text_region
from src.util.logging import NamedLoggerAdapter
from src.util.paths import LocalPaths
from src.util.status import FileStatus
from src.util.types import FormLinkingMethod

from . import validation
from ..database.processed_fields.processed_field_group import ProcessedFieldGroup

logger = logging.getLogger(__name__)


class ProcessWorker(QObject):
    updateStatus = pyqtSignal(int, FileStatus)
    processingComplete = pyqtSignal(int)

    def __init__(self, job_id: int, file_id: int, mutex: QMutex):
        super().__init__()
        self.mutex = mutex
        self._job_id = job_id
        self._file_id = file_id

        self.log = NamedLoggerAdapter(logger, f'Thread: {file_id}')

    def process_text_field(
            self,
            session: requests.Session,
            field: TextField,
            aligned_image: np.ndarray,
            roi_dest_path: Path,
            linking_method: FormLinkingMethod,
            current_region: ProcessedRegion,
            identifier_field: ProcessedTextField | None = None,
    ) -> tuple[bool, ProcessedTextField]:
        # shortcut if this is a synthetic field
        if field.synthetic_only:
            return False, ProcessedTextField(
                name=field.name,
                roi_path=roi_dest_path,
                text='',
                ocr_text='',
                from_controlled_language=None,
                copied_from_linked=None,
                linked_field_id=None,
                validation_result=validation.validate_text_field(field, ''),
                text_field=field,
            )

        # Snip and save off the ROI image
        process_util.snip_roi_image(aligned_image, field.visual_region, save_path=roi_dest_path)

        ocr_region = field.visual_region

        # Check if we need to change the region we OCR
        force_ocr = False
        roi_image = None
        if field.text_regions is not None:
            if len(field.text_regions) == 1:
                ocr_region = field.text_regions[0]
            else:
                # Multiline images need to be stitched together for OCR
                ocr_region = None
                roi_image = process_util.stitch_images(aligned_image, field.text_regions)
                force_ocr = any(
                    [process_util.should_ocr_region(aligned_image, region) for region in field.text_regions]
                )

        ocr_error = False
        from_controlled_language = False if field.checkbox_region is not None else None
        if field.checkbox_region is not None and process_util.get_checked(aligned_image, field.checkbox_region):
            assert field.checkbox_text is not None
            self.log.info(f'Detected checked default option, using: {field.checkbox_text}')
            ocr_result = field.checkbox_text
            from_controlled_language = True
        elif force_ocr or process_util.should_ocr_region(aligned_image, ocr_region):
            ocr_result = ocr_text_region(
                session,
                aligned_image,
                ocr_region,
                roi_image=roi_image,
                add_border=True,
            )
            ocr_error = ocr_result is None
            self.log.info(f'OCR returned: "{ocr_result}"')
        else:
            self.log.info(f'Detected mostly white image, skipping OCR')
            ocr_result = ''

        # OCR result should not be None even if we had an error
        ocr_result = '' if ocr_error else ocr_result

        # Check if we should search for a linking field
        copied_from_linked = False if field.allow_copy else None
        linked_field_id = None
        if field.allow_copy:
            link_field = process_util.locate_linked_field(
                link_method=linking_method,
                current_field=field,
                current_region=current_region,
                identifier_field=identifier_field,
            )

            if link_field is None:
                self.log.warning(f'Failed to locate a field to link to')
            else:
                self.log.info(f'Located linked field: {link_field.name} ({link_field.id}) -> "{link_field.text}"')
                linked_field_id = link_field.id

                if process_util.should_copy_from_previous(ocr_result):
                    copied_from_linked = True
                    ocr_result = link_field.text

        # Validate the field
        validation_result = validation.validate_text_field(field, ocr_result, allow_fuzzy=True)
        self.log.info(f'Validation: {validation_result.result}')

        text = ocr_result
        if validation_result.correction is not None:
            self.log.info(f'Validation correction: "{ocr_result}" -> "{validation_result.correction}"')
            text = validation_result.correction

        field = ProcessedTextField(
            name=field.name,
            roi_path=roi_dest_path,
            text=text,
            ocr_text=ocr_result,
            from_controlled_language=from_controlled_language,
            copied_from_linked=copied_from_linked,
            linked_field_id=linked_field_id,
            validation_result=validation_result,
            text_field=field,
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
            validation_result=ValidationResult(result=None, explanation=None),
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
        self.log.info(f'Validation: {validation_result.result}')

        field = ProcessedMultiCheckboxField(
            name=field.name,
            roi_path=roi_dest_path,
            validation_result=validation_result,
            multi_checkbox_field=field,
            checkboxes=checkboxes,
        )
        return ocr_error, field

    def process_circled_field(
            self,
            field: CircledField,
            aligned_image: np.ndarray,
            roi_dest_path: Path,
    ) -> tuple[bool, ProcessedCircledField]:
        process_util.snip_roi_image(aligned_image, field.visual_region, save_path=roi_dest_path)

        options: dict[str, ProcessedCircledOption] = {}
        for option in field.options:
            # checked = process_util.get_checked(aligned_image, checkbox.region)
            # self.log.info(f'Checkbox "{checkbox.name}" = {checked}')

            options[option.name] = ProcessedCircledOption(
                name=option.name,
                circled=False,
                circled_option=option,
            )

        # # Validate the field
        # validation_result = validation.validate_multi_checkbox_field(field, checkboxes)
        # self.log.info(f'Validation: {validation_result.result}')

        field = ProcessedCircledField(
            name=field.name,
            roi_path=roi_dest_path,
            # validation_result=validation_result,
            circled_field=field,
            options=options,
        )
        return False, field

    @pyqtSlot()
    def start(self) -> None:
        locker = QMutexLocker(self.mutex)
        self.log.info('Staring thread')

        with Session(DB_ENGINE) as session:
            job = session.get(Job, self._job_id)
            input_file = session.get(InputFile, self._file_id)

            # do not process container files
            if input_file.container_file:
                self.log.info('File is marked as a container file, skipping')
                self.processingComplete.emit(input_file.id)
                return

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
                processed_region = ProcessedRegion(
                    local_id=page_region.local_id,
                    name=page_region.name,
                    linking_identifier=None,
                )
                result.regions[processed_region.local_id] = processed_region

                # TODO: we should find and process the identifier field first no matter where it is

                for group in page_region.groups:
                    self.log.info(f'Processing group: "{group.name}"')
                    processed_field_group = ProcessedFieldGroup(name=group.name)
                    processed_region.groups.append(processed_field_group)

                    for field in group.fields:
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
                                current_region=processed_region,
                                identifier_field=identifier_field,
                            )

                            # Save off the identifier field for later linking use
                            if field.identifier:
                                self.log.info(f'Located identifier field: {field.text_field.name}')
                                processed_region.linking_identifier = process_util.extract_identifier(
                                    field.identifier_regex,
                                    result_field.text,
                                )

                            processed_field.processing_error = had_error
                            processed_field.text_field = result_field

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

                        elif field.circled_field is not None:
                            self.log.info(f'Processing Circled Field: {field.circled_field.name}')
                            had_error, result_field = self.process_circled_field(
                                field=field.circled_field,
                                aligned_image=aligned_image,
                                roi_dest_path=roi_path,
                            )

                            processed_field.processing_error = had_error
                            processed_field.circled_field = result_field

                        else:
                            self.log.error(f'Form field had no parts to process')
                            processed_field.processing_error = True

                        # Add the processed field to our region
                        processing_error = processed_field.processing_error
                        processed_field_group.fields.append(processed_field)

            # Commit the results to the DB and signal out that our status is changed
            session.commit()
            self.updateStatus.emit(input_file.id, FileStatus.SUCCESS if not processing_error else FileStatus.FAILED)
            self.processingComplete.emit(input_file.id)
