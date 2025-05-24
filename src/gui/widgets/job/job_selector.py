import uuid
from typing import NamedTuple

from PyQt6.QtCore import pyqtSlot, Qt
from PyQt6.QtWidgets import QRadioButton, QVBoxLayout, QLabel, QWidget, QHBoxLayout, QPushButton, QDialog, QLineEdit

from .existing_job_tree import ExistingJobTree


class JobDetails(NamedTuple):
    db_id: int | None
    job_name: str | None


class JobSelector(QDialog):
    def __init__(self, parent: QWidget, allow_new_jobs: bool = True):
        super().__init__(parent)
        self.setWindowTitle('Job Selection')
        self.setMinimumWidth(450)

        self.new_job_button = QRadioButton('Create a new job', self)
        self.new_job_name = QLineEdit()
        self.new_job_name.setPlaceholderText(str(uuid.uuid4()))

        self.existing_job_button = QRadioButton('Continue an existing job', self)
        self.existing_jobs = ExistingJobTree()

        self.start_button = QPushButton('Start')
        self.start_button.pressed.connect(self.accept)

        self.new_job_button.setChecked(True)
        self.new_job_button.toggled.connect(self.toggle_visibility)
        self.existing_job_button.toggled.connect(self.toggle_visibility)

        # Disable selecting existing jobs if there are none loaded
        if not self.existing_jobs.get_job_count():
            self.existing_job_button.setDisabled(True)
            self.existing_jobs.setDisabled(True)

        if not allow_new_jobs:
            self.new_job_button.setDisabled(True)
            self.new_job_name.setDisabled(True)
            self.existing_job_button.setChecked(True)

        self._set_up_layout()

    def _set_up_layout(self) -> None:
        layout = QVBoxLayout()
        layout.addWidget(self.new_job_button)

        job_name_layout = QHBoxLayout()
        job_name_layout.addWidget(QLabel('Job Name: '))
        job_name_layout.addWidget(self.new_job_name)
        layout.addLayout(job_name_layout)

        divider_layout = QHBoxLayout()
        divider_layout.addStretch()
        divider_layout.addWidget(QLabel('- OR -'))
        divider_layout.addStretch()
        layout.addLayout(divider_layout)

        layout.addWidget(self.existing_job_button)
        layout.addWidget(self.existing_jobs)

        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(self.start_button)
        layout.addLayout(button_layout)

        self.setLayout(layout)

    @pyqtSlot()
    def toggle_visibility(self) -> None:
        self.new_job_name.setDisabled(self.existing_job_button.isChecked())
        self.existing_jobs.setDisabled(self.new_job_button.isChecked())

    def get_selected_job(self) -> JobDetails:
        if self.new_job_button.isChecked():
            return JobDetails(
                db_id=None,
                job_name=self.new_job_name.text() if self.new_job_name.text() else self.new_job_name.placeholderText(),
            )
        else:
            return JobDetails(
                db_id=self.existing_jobs.get_selected_job_id(),
                job_name=None,
            )
