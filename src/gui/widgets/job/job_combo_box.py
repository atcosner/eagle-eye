from sqlalchemy import select
from sqlalchemy.orm import Session

from PyQt6.QtWidgets import QComboBox, QWidget

from src.database import DB_ENGINE
from src.database.job import Job


class JobComboBox(QComboBox):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        # load all existing jobs as possible choices
        self._populate_jobs()

    def _populate_jobs(self) -> None:
        with Session(DB_ENGINE) as session:
            for row in session.execute(select(Job)):
                self.addItem(row.Job.name, row.Job.id)
