import logging
import uuid
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import func

from src.database import DB_ENGINE
from src.database.job import Job
from src.util.paths import LocalPaths

from .base import BaseWindow
from .job_selector import JobDetails, JobSelector
from ..widgets.job_manager import JobManager

logger = logging.getLogger(__name__)


def create_job(job_name: str) -> int:
    with Session(DB_ENGINE) as session:
        new_job = Job(name=job_name, uuid=uuid.uuid4())
        session.add(new_job)
        session.commit()

        LocalPaths.set_up_job_directory(new_job.uuid)

        logger.info(f'Created new job with ID: {new_job.id}')
        return new_job.id


def get_latest_job_id() -> int:
    with Session(DB_ENGINE) as session:
        return session.execute(select(func.max(Job.id))).fetchone()[0]


class MainWindow(BaseWindow):
    def __init__(self):
        super().__init__(None, 'Form Processing')
        self.job_widget = JobManager()

        self._set_up_layout()

    def _set_up_layout(self) -> None:
        self.setMinimumHeight(700)
        self.setMinimumWidth(1100)
        self.setCentralWidget(self.job_widget)

    def start(
            self,
            auto_new_job: bool = False,
            load_latest_job: bool = False,
    ) -> None:
        self.show()

        if auto_new_job:
            details = JobDetails(db_id=None, job_name=str(uuid.uuid4()))
        elif load_latest_job:
            details = JobDetails(db_id=get_latest_job_id(), job_name=None)
        else:
            selector = JobSelector(self)
            if not selector.exec():
                return

            details = selector.get_selected_job()

        # Determine if we are creating a new job or loading one
        logger.info(f'Selected job: {details}')
        if details.db_id is None:
            job_id = create_job(details.job_name)
            self.job_widget.load_job(job_id)
        else:
            self.job_widget.load_job(details.db_id)
