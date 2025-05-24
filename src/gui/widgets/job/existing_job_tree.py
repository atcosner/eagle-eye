from sqlalchemy import select
from sqlalchemy.orm import Session

from PyQt6.QtWidgets import QTreeWidget, QHeaderView, QTreeWidgetItem

from src.database import DB_ENGINE
from src.database.job import Job


class ExistingJobTree(QTreeWidget):
    def __init__(self):
        super().__init__()

        self.setDisabled(True)
        self.setColumnCount(3)
        self.setHeaderLabels(['ID', 'Job Name', 'Status'])
        self.header().setStretchLastSection(False)
        self.header().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)

        self.populate_jobs()

    def populate_jobs(self) -> None:
        with Session(DB_ENGINE) as session:
            for row in session.execute(select(Job)):
                job_item = QTreeWidgetItem()
                job_item.setText(0, str(row.Job.id))
                job_item.setText(1, row.Job.name)
                job_item.setText(2, row.Job.get_status_str())
                self.addTopLevelItem(job_item)

        # If we loaded jobs, select the most recent one
        if self.get_job_count():
            self.setCurrentItem(self.topLevelItem(self.topLevelItemCount() - 1))

    def get_job_count(self) -> int:
        return self.topLevelItemCount()

    def get_selected_job_id(self) -> int | None:
        selected_items = self.selectedItems()
        return int(selected_items[0].text(0)) if selected_items else None
