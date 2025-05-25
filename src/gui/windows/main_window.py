import logging
import uuid

from PyQt6.QtCore import pyqtSlot
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import func

from src.database import DB_ENGINE
from src.database.job import Job
from src.util.paths import LocalPaths

from .base import BaseWindow
from ..dialogs.about_us import AboutUs
from ..dialogs.job_selector import JobDetails, JobSelector
from ..dialogs.reference_form_selctor import ReferenceFormSelector
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
        self._create_menu_bar()

    def _set_up_layout(self) -> None:
        self.setMinimumHeight(700)
        self.setMinimumWidth(1100)
        self.setCentralWidget(self.job_widget)

    def _create_menu_bar(self) -> None:
        file_menu = self.menuBar().addMenu('File')
        file_menu.addAction('New Job').triggered.connect(lambda: self.handle_change_job(True))
        file_menu.addAction('Open Job').triggered.connect(lambda: self.handle_change_job(False))
        file_menu.addSeparator()
        file_menu.addAction('Exit').triggered.connect(self.close)

        form_menu = self.menuBar().addMenu('Reference Form')
        form_menu.addAction('View Reference Forms').triggered.connect(lambda: ReferenceFormSelector(self).exec())
        form_menu.addSeparator()
        form_menu.addAction('Create New Reference Form').triggered.connect(self.handle_create_reference_form)
        form_menu.addAction('Edit Current Reference Form').triggered.connect(self.handle_edit_current_reference_form)

        help_menu = self.menuBar().addMenu('Help')
        help_menu.addAction('About').triggered.connect(lambda: AboutUs(self).exec())

    @pyqtSlot()
    def handle_change_job(self, allow_new_jobs: bool) -> None:
        selector = JobSelector(self, allow_new_jobs=allow_new_jobs)
        if not selector.exec():
            return

        self.load_job(selector.get_selected_job())

    @pyqtSlot()
    def handle_edit_current_reference_form(self) -> None:
        form_id = self.job_widget.get_current_reference_form_id()
        if form_id is not None:
            # TODO: open the form editor
            pass

    @pyqtSlot()
    def handle_create_reference_form(self) -> None:
        # TODO: open the form creation wizard
        pass

    def load_job(self, details: JobDetails) -> None:
        logger.info(f'Loading job: {details}')
        if details.db_id is None:
            job_id = create_job(details.job_name)
            self.job_widget.load_job(job_id)
        else:
            self.job_widget.load_job(details.db_id)

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
            selector = JobSelector(self, allow_new_jobs=True)
            if not selector.exec():
                return
            details = selector.get_selected_job()

        self.load_job(details)
