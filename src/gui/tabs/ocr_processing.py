from sqlalchemy.orm import Session

from PyQt6.QtCore import pyqtSlot
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QCheckBox, QPushButton, QHBoxLayout

from src.database import DB_ENGINE
from src.database.job import Job
from src.util.resources import GENERIC_ICON_PATH
from src.util.settings import SettingsManager

from ..widgets.file_status_list import FileStatusList, FileStatusItem
from ...util.types import FileDetails


class OcrProcessing(QWidget):
    def __init__(self):
        super().__init__()
        self._job_db_id: int | None = None

        self.status_list = FileStatusList()
        # self.status_list.currentItemChanged.connect(self.selected_file_changed)

        self.auto_process = QCheckBox('Process All')
        self.auto_process.setChecked(True)
        self.auto_process.checkStateChanged.connect(self.update_button_text)

        self.process_file_button = QPushButton('Process Files')
        #self.process_file_button.pressed.connect(self.start_pre_processing)

        self._set_up_layout()
        self._check_api_config()

    def _set_up_layout(self) -> None:
        layout = QVBoxLayout()
        layout.addWidget(self.status_list)
        # layout.addWidget(self.details)

        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(self.auto_process)
        button_layout.addWidget(self.process_file_button)
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def _check_api_config(self) -> None:
        valid_config = SettingsManager().valid_api_config()
        self.auto_process.setDisabled(not valid_config)
        self.process_file_button.setDisabled(not valid_config)

        # Update the button icon
        if valid_config:
            self.process_file_button.setToolTip(None)
            self.process_file_button.setIcon(QIcon())
        else:
            self.process_file_button.setToolTip('The Google Vision API is not configured')
            self.process_file_button.setIcon(QIcon(str(GENERIC_ICON_PATH / 'bad.png')))

    @pyqtSlot()
    def update_button_text(self) -> None:
        text = 'Process File'
        if self.auto_process.isChecked():
            text += 's'

        self.process_file_button.setText(text)

    def load_job(self, job: Job | int) -> None:
        self.status_list.clear()

        with Session(DB_ENGINE) as session:
            job = session.get(Job, job) if isinstance(job, int) else job
            self._job_db_id = job.id

            for input_file in job.input_files:
                # Only add files that have been pre-processed successfully
                if input_file.pre_process_result is None:
                    continue

                if not input_file.pre_process_result.successful_alignment:
                    continue

                self.status_list.add_file(
                    FileDetails(
                        db_id=input_file.id,
                        path=input_file.path,
                    )
                )
