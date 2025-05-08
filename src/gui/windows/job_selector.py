import uuid
from sqlalchemy import select
from sqlalchemy.orm import Session
from typing import NamedTuple

from PyQt6.QtCore import pyqtSlot, Qt
from PyQt6.QtWidgets import (
    QRadioButton, QVBoxLayout, QLabel, QWidget, QHBoxLayout, QPushButton, QDialog,
    QLineEdit, QTreeWidget, QTreeWidgetItem, QHeaderView,
)

from src.database import DB_ENGINE
from src.database.job import Job


class JobDetails(NamedTuple):
    db_id: int | None
    job_name: str | None


class JobSelector(QDialog):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setWindowTitle('Job Selection')
        self.setMinimumWidth(450)

        self.new_job_button = QRadioButton('Create a new job', self)
        self.new_job_name = QLineEdit()
        self.new_job_name.setPlaceholderText(str(uuid.uuid4()))

        self.existing_job_button = QRadioButton('Continue an existing job', self)

        self.existing_job_list = QTreeWidget()
        self.existing_job_list.setDisabled(True)
        self.existing_job_list.setColumnCount(3)
        # self.existing_job_list.setSelectionMode(QAbstractItemView.SingleSelection)
        self.existing_job_list.setHeaderLabels(['ID', 'Job Name', 'Status'])
        self.existing_job_list.header().setStretchLastSection(False)
        self.existing_job_list.header().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)

        self.start_button = QPushButton('Start')
        self.start_button.pressed.connect(self.accept)

        self.new_job_button.setChecked(True)
        self.new_job_button.toggled.connect(self.toggle_visibility)
        self.existing_job_button.toggled.connect(self.toggle_visibility)

        self._set_up_layout()
        self._populate_jobs()

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
        layout.addWidget(self.existing_job_list)

        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(self.start_button)
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def _populate_jobs(self) -> None:
        with Session(DB_ENGINE) as session:
            for row in session.execute(select(Job)):
                job_item = QTreeWidgetItem()
                job_item.setText(0, str(row.Job.id))
                job_item.setText(1, row.Job.name)
                job_item.setText(2, '<NO STATUS>')
                self.existing_job_list.addTopLevelItem(job_item)

        # Disable the existing job widgets if we loaded no jobs
        if self.existing_job_list.topLevelItemCount() == 0:
            self.existing_job_button.setDisabled(True)
            self.existing_job_list.setDisabled(True)
        else:
            # Select the newest job
            self.existing_job_list.setCurrentItem(
                self.existing_job_list.topLevelItem(self.existing_job_list.topLevelItemCount() - 1)
            )

    @pyqtSlot()
    def toggle_visibility(self) -> None:
        self.new_job_name.setDisabled(self.existing_job_button.isChecked())
        self.existing_job_list.setDisabled(self.new_job_button.isChecked())

    def get_selected_job(self) -> JobDetails:
        if self.new_job_button.isChecked():
            return JobDetails(
                db_id=None,
                job_name=self.new_job_name.text() if self.new_job_name.text() else self.new_job_name.placeholderText(),
            )
        else:
            selected_job = self.existing_job_list.selectedItems()[0]
            return JobDetails(
                db_id=int(selected_job.text(0)),
                job_name=None,
            )
