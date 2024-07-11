import logging
from datetime import datetime
from enum import Enum, auto
from werkzeug.datastructures import FileStorage
from pathlib import Path

logger = logging.getLogger(__name__)


class JobState(Enum):
    CREATED = auto()
    FILES_SUBMITTED = auto()
    PRE_PROCESSING = auto()
    PROCESSING = auto()

    # Terminal states
    COMPLETED = auto()
    ERROR = auto()


class Job:
    def __init__(self, parent_directory: Path, job_id: str):
        self.job_id: str = job_id
        self.states: list[tuple[JobState, datetime]] = [(JobState.CREATED, datetime.now())]
        self.exception: Exception | None = None

        # Create a working directory for ourselves
        self.working_dir: Path = parent_directory / job_id
        logger.info(f'Job working directory: {self.working_dir}')
        try:
            self.working_dir.mkdir()
        except Exception as e:
            self._record_exception(e)

    def _change_state(self, state: JobState) -> None:
        self.states.append((state, datetime.now()))

    def _record_exception(self, exception: Exception) -> None:
        logger.exception('Encountered exception')
        self.exception = exception
        self._change_state(JobState.ERROR)

    def save_files(self, files: list[FileStorage]) -> None:
        for file in files:
            # Handle empty FileStorage objects
            if not file.filename:
                logger.warning('Received file without name')
                continue

            file_path = self.working_dir / file.filename
            logger.info(f'Saving: {file.filename} ({file_path})')

            try:
                file.save(file_path)
            except Exception as e:
                self._record_exception(e)
                return

        self._change_state(JobState.FILES_SUBMITTED)
