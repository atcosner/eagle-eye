import logging
import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from PyQt6.QtWidgets import QWidget, QTabWidget, QVBoxLayout, QLineEdit, QHBoxLayout, QLabel, QComboBox, QSizePolicy

from src.database import DB_ENGINE
from src.database.job import Job
from src.database.reference_form import ReferenceForm

from .base import BaseWindow
from .job_selector import JobSelector
from ..tabs.file_picker import FilePicker
from ..tabs.file_pre_processing import FilePreProcessing

logger = logging.getLogger(__name__)


def create_job(job_name: str) -> int:
    with Session(DB_ENGINE) as session:
        new_job = Job(name=job_name, uuid=uuid.uuid4())
        session.add(new_job)
        session.commit()

        logger.info(f'Created new job with ID: {new_job.id}')
        return new_job.id


class MainWindow(BaseWindow):
    def __init__(self):
        super().__init__(None, 'Form Processing')

        self.picker = FilePicker()
        self.pre_processing = FilePreProcessing()

        self.job_name = QLineEdit(self)
        self.job_name.setDisabled(True)

        self.job_reference = QComboBox(self)
        self.job_reference.setPlaceholderText('< No Reference Form Selected >')
        size_policy = QSizePolicy()
        size_policy.setHorizontalPolicy(QSizePolicy.Policy.MinimumExpanding)
        self.job_reference.setSizePolicy(size_policy)

        self.tabs = QTabWidget(self)
        self.tabs.addTab(self.picker, 'Step 1 - Choose Files')
        self.tabs.addTab(self.pre_processing, 'Step 2 - Pre-Processing')

        self._connect_signals()
        self._set_layout()

    def _connect_signals(self) -> None:
        self.picker.filesConfirmed.connect(self.pre_processing.add_files)

    def _set_layout(self) -> None:
        job_name_layout = QHBoxLayout()
        job_name_layout.addWidget(QLabel('Job Name: '))
        job_name_layout.addWidget(self.job_name)

        job_reference_layout = QHBoxLayout()
        job_reference_layout.addWidget(QLabel('Reference Form: '))
        job_reference_layout.addWidget(self.job_reference)

        layout = QVBoxLayout()
        layout.addLayout(job_name_layout)
        layout.addLayout(job_reference_layout)
        layout.addSpacing(15)
        layout.addWidget(self.tabs)

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

    def load_job(self, job_id: int) -> None:
        with Session(DB_ENGINE) as session:
            job = session.get(Job, job_id)
            self.job_name.setText(job.name)

    def reload_reference_forms(self) -> None:
        self.job_reference.clear()
        with Session(DB_ENGINE) as session:
            for row in session.execute(select(ReferenceForm)):
                self.job_reference.addItem(row.ReferenceForm.name)

    def start(self) -> None:
        self.reload_reference_forms()
        self.show()

        selector = JobSelector(self)
        if not selector.exec():
            self.close()

        # Determine if we are creating a new job or loading one
        details = selector.get_selected_job()
        logger.info(f'Selected job: {details}')
        if details.db_id is None:
            job_id = create_job(details.job_name)
            self.load_job(job_id)
        else:
            self.load_job(details.db_id)
