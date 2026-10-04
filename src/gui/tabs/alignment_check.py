from PyQt6.QtCore import pyqtSlot, Qt
from PyQt6.QtWidgets import QTreeWidgetItemIterator, QVBoxLayout, QHBoxLayout, QSplitter
from sqlalchemy.orm import Session

from src.database import DB_ENGINE
from src.database.job import Job
from src.util.status import FileStatus, is_finished

from .processing_step import ProcessingStep
from ..widgets.alignment_check_details import AlignmentCheckDetails
from ..widgets.file.file_status_list import FileStatusItem, ListMode


class AlignmentCheck(ProcessingStep):
    def __init__(self):
        super().__init__(
            step_button_text='Check Alignment',
            details_cls=AlignmentCheckDetails,
        )

        self.details: AlignmentCheckDetails = self.step_details
        self.details.alignmentConfirmed.connect(self.alignment_confirmed)

    def _set_up_layout(self) -> None:
        # Show the file list and the overlaid image side by side
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(self.file_list)
        splitter.addWidget(self.step_details)

        # Give the overlaid image most of the space
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 3)

        layout = QVBoxLayout()
        layout.addWidget(splitter)

        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(self.auto_process)
        button_layout.addWidget(self.process_file_button)
        button_layout.addWidget(self.continue_button)
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def _leaf_items(self) -> list[FileStatusItem]:
        # Container files have no alignment of their own, only their children do
        items = []
        iterator = QTreeWidgetItemIterator(self.file_list)
        while iterator.value():
            if not iterator.value().childCount():
                items.append(iterator.value())
            iterator += 1

        return items

    def load_job(self, job: Job | int | None) -> None:
        super().load_job(job)
        self.details.clear_confirmations()
        if job is None:
            return

        with Session(DB_ENGINE) as session:
            job = session.get(Job, job) if isinstance(job, int) else job
            self._job_db_id = job.id

            self.file_list.load_job(ListMode.ALIGNMENT_CHECK, job)

        # Run GUI updates based if all our items are complete
        self.update_control_state()
        self.select_next_pending()

    def set_view_only(self, view_only: bool) -> None:
        super().set_view_only(view_only)
        self.details.set_view_only(view_only)

    def update_control_state(self) -> None:
        # Nothing to process in this step, the user confirms each file instead
        self.auto_process.setVisible(False)
        self.process_file_button.setVisible(False)
        self.continue_button.setVisible(self.all_items_processed())

    def all_items_processed(self) -> bool:
        items = self._leaf_items()
        return bool(items) and all(is_finished(item.get_status()) for item in items)

    def select_next_pending(self) -> None:
        for item in self._leaf_items():
            if not is_finished(item.get_status()):
                self.file_list.setCurrentItem(item)
                return

    @pyqtSlot(int)
    def alignment_confirmed(self, db_id: int) -> None:
        self.worker_status_update(db_id, FileStatus.SUCCESS)
        self.update_control_state()
        self.select_next_pending()

    def start_worker(self, item: FileStatusItem) -> None:
        # Nothing to process, this step only views the alignment results
        pass
