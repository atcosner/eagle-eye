from PyQt6.QtCore import pyqtSlot, Qt
from PyQt6.QtWidgets import QTreeWidgetItemIterator, QMessageBox, QVBoxLayout, QHBoxLayout, QSplitter
from sqlalchemy.orm import Session

from src.database import DB_ENGINE
from src.database.job import Job
from src.processing.alignment_refine_worker import AlignmentRefineWorker
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
        self.details.alignmentRefineRequested.connect(self.refine_alignment)

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
        if job is None:
            return

        with Session(DB_ENGINE) as session:
            job = session.get(Job, job) if isinstance(job, int) else job
            self._job_db_id = job.id

            self.file_list.load_job(ListMode.ALIGNMENT_CHECK, job)

        # Run GUI updates based if all our items are complete
        self.update_control_state()

        # Hide the details until a file is selected, which only happens here if a file needs confirming
        self.file_list.setCurrentItem(None)
        self.details.reset()
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

    @pyqtSlot(int)
    def refine_alignment(self, db_id: int) -> None:
        assert self._job_db_id is not None, 'Attempt to refine alignment without a Job ID'
        if self.threads:
            return

        item = self.file_list.find_item(db_id)
        if item is None:
            return

        self.worker_status_update(db_id, FileStatus.IN_PROGRESS)
        self.details.set_refining(db_id)
        self.update_control_state()

        worker = AlignmentRefineWorker(self._job_db_id, db_id, self.thread_mutex)
        worker.updateStatus.connect(self.worker_status_update)
        worker.refinementFailed.connect(self.refinement_failed)
        worker.processingComplete.connect(self.worker_complete)

        self.start_thread(item, worker)

    @pyqtSlot(int)
    def refinement_failed(self, db_id: int) -> None:
        QMessageBox.warning(
            self,
            'Re-run Alignment',
            'The alignment could not be improved, the previous alignment was kept.',
        )

    @pyqtSlot(int)
    def worker_complete(self, db_id: int) -> None:
        self.details.set_refining(None)
        super().worker_complete(db_id)

    def start_worker(self, item: FileStatusItem) -> None:
        # Nothing to process, this step only views the alignment results
        pass
