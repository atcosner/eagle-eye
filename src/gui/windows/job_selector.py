from sqlalchemy import select
from sqlalchemy.orm import Session

from PyQt6.QtCore import pyqtSlot
from PyQt6.QtWidgets import QRadioButton, QVBoxLayout, QLabel, QWidget, QHBoxLayout, QListWidget

from src.database import DB_ENGINE
from src.database.job import Job

from .base import BaseWindow


class JobSelector(BaseWindow):
    def __init__(self):
        super().__init__('Job Selection')

        self.new_job_button = QRadioButton('Create a new job', self)
        self.existing_job_button = QRadioButton('Continue an existing job', self)
        self.existing_job_list = QListWidget()

        self.new_job_button.setChecked(True)
        self.existing_job_list.setDisabled(True)
        self.existing_job_button.pressed.connect(self.toggle_job_list_visibility)

        self._set_up_layout()
        self._populate_jobs()

    def _set_up_layout(self) -> None:
        layout = QVBoxLayout()
        layout.addWidget(self.new_job_button)

        divider_layout = QHBoxLayout()
        divider_layout.addStretch()
        divider_layout.addWidget(QLabel('- OR -'))
        divider_layout.addStretch()
        layout.addLayout(divider_layout)

        layout.addWidget(self.existing_job_button)
        layout.addWidget(self.existing_job_list)

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

    def _populate_jobs(self) -> None:
        with Session(DB_ENGINE) as session:
            for row in session.execute(select(Job)):
                self.existing_job_list.addItem(row.Job.name)

    @pyqtSlot()
    def toggle_job_list_visibility(self) -> None:
        self.existing_job_list.setDisabled(self.new_job_button.isChecked())
