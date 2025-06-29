from sqlalchemy import select
from sqlalchemy.orm import Session

from PyQt6.QtCore import pyqtSlot, Qt
from PyQt6.QtWidgets import QWidget, QComboBox, QSizePolicy, QLineEdit, QHBoxLayout, QLabel, QVBoxLayout, QPushButton

from src.database import DB_ENGINE
from src.database.job import Job
from src.database.reference_form import ReferenceForm

from .processing_pipeline import ProcessingPipeline
from ..windows.reference_form_editor import ReferenceFormEditor


class JobManager(QWidget):
    def __init__(self):
        super().__init__()
        self._job_db_id: int | None = None
        self._reference_form_db_id: int | None = None

        self.job_name = QLineEdit(self)
        self.job_name.setDisabled(True)

        self.reference_form_selector = QComboBox(self)
        self.reference_form_selector.setPlaceholderText('< No Reference Form Selected >')
        size_policy = QSizePolicy()
        size_policy.setHorizontalPolicy(QSizePolicy.Policy.MinimumExpanding)
        self.reference_form_selector.setSizePolicy(size_policy)
        self.reference_form_selector.currentIndexChanged.connect(self.handle_reference_form_change)

        self.view_button = QPushButton('View')
        self.view_button.pressed.connect(self.handle_view_reference_form)

        self.processing_pipeline = ProcessingPipeline(self)
        self.processing_pipeline.inputFilesConfirmed.connect(self.handle_input_files_confirmed)

        self._set_layout()
        self._toggle_controls(False)
        self.reload_reference_forms()

    def _set_layout(self) -> None:
        job_name_layout = QHBoxLayout()
        job_name_layout.addWidget(QLabel('Job Name: '))
        job_name_layout.addWidget(self.job_name)

        job_reference_layout = QHBoxLayout()
        job_reference_layout.addWidget(QLabel('Reference Form: '))
        job_reference_layout.addWidget(self.reference_form_selector)
        job_reference_layout.addWidget(self.view_button)

        layout = QVBoxLayout()
        layout.addLayout(job_name_layout)
        layout.addLayout(job_reference_layout)
        layout.addSpacing(15)
        layout.addWidget(self.processing_pipeline)
        self.setLayout(layout)

    def _toggle_controls(self, enabled: bool) -> None:
        self.reference_form_selector.setDisabled(not enabled)
        self.processing_pipeline.setDisabled(not enabled)

    def get_current_reference_form_id(self) -> int | None:
        return self._reference_form_db_id

    def update_current_reference_form(self, form_id: int | None) -> None:
        print('update', self._reference_form_db_id, form_id)
        self._reference_form_db_id = form_id
        self.processing_pipeline.change_reference_form(form_id)

        # select the reference form in the combo box
        for index in range(self.reference_form_selector.count()):
            if self.reference_form_selector.itemData(index) == form_id:
                self.reference_form_selector.setCurrentIndex(index)

    @pyqtSlot()
    def handle_input_files_confirmed(self) -> None:
        self.reference_form_selector.setDisabled(True)

    @pyqtSlot(int)
    def handle_reference_form_change(self, _: int) -> None:
        self.update_current_reference_form(self.reference_form_selector.currentData())

    @pyqtSlot()
    def handle_view_reference_form(self) -> None:
        if self._reference_form_db_id is None:
            return

        form_viewer = ReferenceFormEditor(self, False, self._reference_form_db_id)
        form_viewer.setWindowModality(Qt.WindowModality.ApplicationModal)
        form_viewer.show()

    def load_job(self, job_id: int) -> None:
        self._toggle_controls(True)

        with Session(DB_ENGINE) as session:
            job = session.get(Job, job_id)
            self._job_db_id = job_id

            # update the current reference form if the job has one selected
            if job.reference_form is not None:
                self.update_current_reference_form(job.reference_form.id)

            self.job_name.setText(job.name)
            self.processing_pipeline.load_job(job_id)

    def reload_reference_forms(self) -> None:
        self.reference_form_selector.clear()
        with Session(DB_ENGINE) as session:
            for row in session.execute(select(ReferenceForm)):
                self.reference_form_selector.addItem(row.ReferenceForm.name, row.ReferenceForm.id)

        if self.reference_form_selector.count() > 0:
            self.reference_form_selector.setCurrentIndex(0)
