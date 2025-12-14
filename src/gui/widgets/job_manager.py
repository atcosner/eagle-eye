from sqlalchemy.orm import Session

from PyQt6.QtWidgets import QWidget, QLineEdit, QHBoxLayout, QLabel, QVBoxLayout

from src.database import DB_ENGINE
from src.database.job import Job

from .processing_pipeline import ProcessingPipeline


class JobManager(QWidget):
    def __init__(self):
        super().__init__()
        self._job_db_id: int | None = None

        self.job_name = QLineEdit(self)
        self.job_name.setDisabled(True)

        self.processing_pipeline = ProcessingPipeline(self)

        self._set_layout()
        self._toggle_controls(False)

    def _set_layout(self) -> None:
        job_name_layout = QHBoxLayout()
        job_name_layout.addWidget(QLabel('Job Name: '))
        job_name_layout.addWidget(self.job_name)

        layout = QVBoxLayout()
        layout.addLayout(job_name_layout)
        layout.addSpacing(15)
        layout.addWidget(self.processing_pipeline)
        self.setLayout(layout)

    def _toggle_controls(self, enabled: bool) -> None:
        self.processing_pipeline.setDisabled(not enabled)

    def load_job(self, job_id: int) -> None:
        self._toggle_controls(True)

        with Session(DB_ENGINE) as session:
            job = session.get(Job, job_id)
            self._job_db_id = job_id

            self.job_name.setText(job.name)
            self.processing_pipeline.load_job(job_id)
