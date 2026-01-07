import logging
import uuid
from pathlib import Path
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import func

from PyQt6.QtCore import pyqtSlot, Qt

from src.database import DB_ENGINE
from src.database.copy import copy_reference_form
from src.database.job import Job
from src.database.reference_form import ReferenceForm
from src.util.paths import LocalPaths
from src.util.types import FormLinkingMethod, FormAlignmentMethod

from .base import BaseWindow
from .reference_form_editor import ReferenceFormEditor
from ..dialogs.about_us import AboutUs
from ..dialogs.bug_reporter import BugReporter
from ..dialogs.job_selector import JobDetails, JobSelector
from ..dialogs.reference_form_importer import ReferenceFormImporter
from ..dialogs.reference_form_selector import ReferenceFormSelector
from ..dialogs.vision_api_config import VisionApiConfig
from ..widgets.job_manager import JobManager
from ..wizards.first_start_wizard import FirstStartWizard
from ..wizards.reference_form_wizard import ReferenceFormWizard

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
        super().__init__(None, title_suffix=None)
        self.job_widget = JobManager()

        self._set_up_layout()
        self._create_menu_bar()
        self._check_first_start()

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
        form_menu.addAction('View Reference Forms').triggered.connect(self.handle_view_reference_form)
        form_menu.addSeparator()
        form_menu.addAction('Create New Reference Form').triggered.connect(self.handle_create_reference_form)
        form_menu.addSeparator()
        form_menu.addAction('Import Reference Forms').triggered.connect(self.handle_import_reference_form)

        settings_menu = self.menuBar().addMenu('Settings')
        settings_menu.addAction('Check Google API Config').triggered.connect(lambda: VisionApiConfig(self).exec())
        # settings_menu.addSeparator()
        # settings_menu.addAction('Edit Settings').triggered.connect(self.handle_create_reference_form)

        help_menu = self.menuBar().addMenu('Help')
        help_menu.addAction('Report A Bug').triggered.connect(lambda: BugReporter(self).exec())
        help_menu.addSeparator()
        help_menu.addAction('About').triggered.connect(lambda: AboutUs(self).exec())

    def _check_first_start(self) -> None:
        with Session(DB_ENGINE) as session:
            job_count = session.query(Job).count()
            reference_form_count = session.query(ReferenceForm).count()
            logger.info(f'Checking first start: {job_count} jobs, {reference_form_count} reference forms')

            # TODO: we could check for the directory structure on disk instead
            if job_count == 0 and reference_form_count == 0:
                self.show()
                FirstStartWizard(self).exec()

                # the wizard could add reference forms, so we need to reload that tab
                self.job_widget.reload_reference_forms()

    @pyqtSlot()
    def handle_change_job(self, allow_new_jobs: bool) -> None:
        selector = JobSelector(self, allow_new_jobs=allow_new_jobs)
        if not selector.exec():
            return

        self.load_job(selector.get_selected_job())

    @pyqtSlot()
    def handle_view_reference_form(self) -> None:
        form_selector = ReferenceFormSelector(self)
        if not form_selector.exec():
            return

        form_id = form_selector.get_selected_form()
        form_builder = ReferenceFormEditor(self, False, form_id)
        form_builder.setWindowModality(Qt.WindowModality.ApplicationModal)
        form_builder.show()

    @pyqtSlot()
    def handle_import_reference_form(self) -> None:
        form_importer = ReferenceFormImporter(self)
        if not form_importer.exec():
            return

        self.job_widget.reload_reference_forms()

    @pyqtSlot()
    def handle_create_reference_form(self) -> None:
        wizard = ReferenceFormWizard(self)
        if not wizard.exec():
            return

        # create a new reference form
        logger.info(f'Creating new reference form: {wizard.field("form.name")}')
        with Session(DB_ENGINE) as session:
            alignment_enum = FormAlignmentMethod[wizard.field('form.align_method')]

            new_form = ReferenceForm(
                name=wizard.field('form.name'),
                path=Path(wizard.field('form.file_path')),
                alignment_method=alignment_enum,
                alignment_mark_count=wizard.field('form.align_marks'),
                linking_method=FormLinkingMethod[wizard.field('form.link_method')],
            )

            # if we are copying another form, copy in all the regions and fields
            if wizard.field('form.copy_existing'):
                copy_form = session.get(ReferenceForm, wizard.field('form.existing_id'))
                copy_reference_form(new_form, copy_form, copy_details=False)

            session.add(new_form)
            session.commit()

        self.job_widget.reload_reference_forms()

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
