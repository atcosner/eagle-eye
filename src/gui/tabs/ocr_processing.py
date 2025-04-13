from sqlalchemy.orm import Session

from PyQt6.QtWidgets import QWidget, QVBoxLayout

from src.database import DB_ENGINE
from src.database.job import Job

from ..widgets.file_status_list import FileStatusList, FileStatusItem
from ...util.types import FileDetails


class OcrProcessing(QWidget):
    def __init__(self):
        super().__init__()
        self._job_db_id: int | None = None

        self.status_list = FileStatusList()
        # self.status_list.currentItemChanged.connect(self.selected_file_changed)

        self._set_up_layout()

    def _set_up_layout(self) -> None:
        layout = QVBoxLayout()
        layout.addWidget(self.status_list)
        # layout.addWidget(self.details)

        # button_layout = QHBoxLayout()
        # button_layout.addStretch()
        # button_layout.addWidget(self.auto_process)
        # button_layout.addWidget(self.process_file_button)
        # layout.addLayout(button_layout)

        self.setLayout(layout)

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
