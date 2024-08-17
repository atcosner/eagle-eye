import logging
import uuid
from dataclasses import dataclass
from datetime import datetime
from enum import Enum, auto
from pathlib import Path
from typing import NamedTuple
from werkzeug.datastructures import FileStorage

from .definitions.ornithology_form import TOP_OCR_FIELDS
from .pre_processing import AlignmentResult, grayscale_image, align_images
from .processing import OcrResult, process_ocr_regions

logger = logging.getLogger(__name__)


class JobState(Enum):
    CREATED = auto()
    FILES_SUBMITTED = auto()
    PRE_PROCESSED = auto()

    # Terminal states
    COMPLETED = auto()
    ERROR = auto()


class StateChange(NamedTuple):
    state: JobState
    timestamp: datetime


@dataclass
class HtmlJobInfo:
    uuid: str
    last_state: JobState
    last_timestamp: datetime


class Job:
    def __init__(self, parent_directory: Path, job_id: uuid.UUID, reference_image_path: Path):
        self.job_id: uuid.UUID = job_id
        self.states: list[StateChange] = [StateChange(JobState.CREATED, datetime.now())]
        self.exception: Exception | None = None

        self.reference_path: Path = reference_image_path
        self.submitted_images: list[Path] = []
        self.alignment_results: list[AlignmentResult] = []
        self.ocr_results: list[list[OcrResult]] = []

        # Create a working directory for ourselves
        self.working_dir: Path = parent_directory / str(job_id)
        logger.info(f'Job working directory: {self.working_dir}')
        try:
            self.working_dir.mkdir()
        except Exception as e:
            self._record_exception(e)

    def _change_state(self, state: JobState) -> None:
        if not self.pending_work():
            logger.warning('Attempting to change state when we are in a terminal state.')
            return

        self.states.append(StateChange(state, datetime.now()))

    def _record_exception(self, exception: Exception) -> None:
        logger.exception('Encountered exception')
        self.exception = exception
        self._change_state(JobState.ERROR)

    def get_current_state(self) -> StateChange:
        return self.states[-1]

    def get_state_changes(self) -> list[StateChange]:
        return self.states

    def to_html_info(self) -> HtmlJobInfo:
        current_state = self.get_current_state()

        return HtmlJobInfo(
            uuid=str(self.job_id),
            last_state=current_state.state,
            last_timestamp=current_state.timestamp,
        )

    def pending_work(self) -> bool:
        return self.get_current_state().state not in [JobState.ERROR, JobState.COMPLETED]

    def continue_processing(self) -> None:
        if not self.pending_work():
            return

        current_state = self.get_current_state().state
        match current_state:
            case JobState.FILES_SUBMITTED:
                self._pre_process()
            case JobState.PRE_PROCESSED:
                self._process_ocr()
            case _:
                logger.warning(f'Unknown state: {current_state}')

    def num_images(self) -> int:
        return len(self.submitted_images)

    def save_files(self, files: list[FileStorage]) -> None:
        idx = 0
        for file in files:
            # Handle empty FileStorage objects
            if not file.filename:
                logger.warning('Received file without name')
                continue

            # Create the directory for this file
            file_dir_path = self.working_dir / str(idx)
            try:
                file_dir_path.mkdir()
            except Exception as e:
                self._record_exception(e)
                continue

            # Save the original file
            # TODO: This should be called something like "original.[EXTENSION]"
            #  (We need a mapping of the original to the new name if we do this. Metadata file? DB row?)
            file_path = file_dir_path / f'original_{file.filename}'
            logger.info(f'Saving: {file.filename} ({file_path})')

            try:
                file.save(file_path)
                self.submitted_images.append(file_path)
            except Exception as e:
                self._record_exception(e)
            finally:
                idx += 1

        self._change_state(JobState.FILES_SUBMITTED)

    def _pre_process(self) -> None:
        for original_path in self.submitted_images:
            logger.info(f'Pre-processing: {original_path}')

            try:
                # Convert the original image to grayscale
                gray_path = grayscale_image(original_path)
                logger.info(f'Converted image to grayscale: {gray_path}')

                # Detect key points in the image
                alignment_result = align_images(gray_path, self.reference_path)

                self.alignment_results.append(alignment_result)
                logger.info(f'Matched features image: {alignment_result.matched_features_image_path}')
                logger.info(f'Overlaid image: {alignment_result.overlaid_image_path}')
                logger.info(f'Aligned image: {alignment_result.aligned_image_path}')
            except Exception as e:
                self._record_exception(e)
                break

        self._change_state(JobState.PRE_PROCESSED)

    def _process_ocr(self) -> None:
        for result in self.alignment_results:
            logger.info(f'Attempting OCR on: {result.aligned_image_path}')

            # Create a directory to store the OCR roi pictures
            working_dir = result.aligned_image_path.parent
            # try:
            #     working_dir.mkdir()
            # except Exception as e:
            #     self._record_exception(e)
            #     continue

            try:
                results = process_ocr_regions(
                    working_dir=working_dir,
                    aligned_image_path=result.aligned_image_path,
                    fields=TOP_OCR_FIELDS,
                )
                self.ocr_results.append(results)
            except Exception as e:
                self._record_exception(e)
                break

        self._change_state(JobState.COMPLETED)
