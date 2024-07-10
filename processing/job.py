import logging
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
        self.state: JobState = JobState.CREATED
        self.exception: Exception | None = None

        # Create a working directory for ourselves
        self.working_dir: Path = parent_directory / job_id
        self.working_dir.mkdir()
        logger.info(f'Job working directory: {self.working_dir}')

    def save_files(self, files: list[FileStorage]) -> None:
        for file in files:
            file_path = self.working_dir / file.filename
            logger.info(f'Saving: {file.filename} ({file_path})')

            try:
                file.save(file_path)
            except Exception as e:
                self.exception = e
                logger.exception('Exception saving file')

                self.state = JobState.ERROR
                return

        self.state = JobState.FILES_SUBMITTED
