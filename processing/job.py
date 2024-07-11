import logging
import uuid
from dataclasses import dataclass
from datetime import datetime
from enum import Enum, auto
from pathlib import Path
from typing import NamedTuple
from werkzeug.datastructures import FileStorage

logger = logging.getLogger(__name__)


class JobState(Enum):
    CREATED = auto()
    FILES_SUBMITTED = auto()
    PRE_PROCESSING = auto()
    PROCESSING = auto()

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
    def __init__(self, parent_directory: Path, job_id: uuid.UUID):
        self.job_id: uuid.UUID = job_id
        self.states: list[StateChange] = [StateChange(JobState.CREATED, datetime.now())]
        self.exception: Exception | None = None

        # Create a working directory for ourselves
        self.working_dir: Path = parent_directory / str(job_id)
        logger.info(f'Job working directory: {self.working_dir}')
        try:
            self.working_dir.mkdir()
        except Exception as e:
            self._record_exception(e)

    def _change_state(self, state: JobState) -> None:
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
