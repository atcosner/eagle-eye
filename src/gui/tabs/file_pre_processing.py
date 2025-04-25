from PyQt6.QtCore import pyqtSlot, QThread, QMutex, pyqtSignal
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QCheckBox, QHBoxLayout, QTreeWidgetItem
from sqlalchemy.orm import Session

from src.database import DB_ENGINE
from src.database.job import Job
from src.processing.pre_process_worker import PreProcessingWorker
from src.util.status import FileStatus, is_finished
from src.util.types import FileDetails

from ..widgets.file_status_list import FileStatusList, FileStatusItem
from ..widgets.pre_processing_details import PreProcessingDetails


class FilePreProcessing(QWidget):
    continueToOcr = pyqtSignal()

    def __init__(self):
        super().__init__()
        self._job_db_id: int | None = None

        self.thread_idx: int = 0
        self.thread_mutex: QMutex = QMutex()
        self.pre_processing_threads: dict[int, tuple[QThread, PreProcessingWorker]] = {}

        self.status_list = FileStatusList()
        self.status_list.currentItemChanged.connect(self.selected_file_changed)

        self.details = PreProcessingDetails()

        self.process_file_button = QPushButton('Pre-Process Files')
        self.process_file_button.pressed.connect(self.start_pre_processing)

        self.auto_process = QCheckBox('Process All')
        self.auto_process.setChecked(True)
        self.auto_process.checkStateChanged.connect(self.update_button_text)

        self.continue_button = QPushButton('Continue')
        self.continue_button.setVisible(False)
        self.continue_button.pressed.connect(self.continueToOcr)

        self._set_up_layout()

    def _set_up_layout(self) -> None:
        layout = QVBoxLayout()
        layout.addWidget(self.status_list)
        layout.addWidget(self.details)

        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(self.auto_process)
        button_layout.addWidget(self.process_file_button)
        button_layout.addWidget(self.continue_button)
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def load_job(self, job: Job | int | None) -> None:
        self.status_list.clear()
        if job is None:
            self._job_db_id = None
            return

        # Check if any of our files had a pre-process result
        with Session(DB_ENGINE) as session:
            job = session.get(Job, job) if isinstance(job, int) else job
            self._job_db_id = job.id

            # Check if any of the files have a pre-processing result
            any_pre_process = any([(input_file.pre_process_result is not None) for input_file in job.input_files])

            # If any files had a pre-processing result, add them all
            if any_pre_process:
                for input_file in job.input_files:
                    # Determine the initial status
                    initial_status = FileStatus.PENDING
                    if input_file.pre_process_result is not None:
                        if input_file.pre_process_result.successful_alignment:
                            initial_status = FileStatus.SUCCESS
                        else:
                            initial_status = FileStatus.FAILED

                    self.status_list.add_file(
                        file=FileDetails(
                            db_id=input_file.id,
                            path=input_file.path,
                        ),
                        initial_status=initial_status,
                    )

        # Run GUI updates based if all our items are complete
        self.threads_complete()

    def all_items_processed(self) -> bool:
        all_done = True
        for idx in range(self.status_list.topLevelItemCount()):
            item = self.status_list.topLevelItem(idx)
            if not is_finished(item.get_status()):
                all_done = False

        return all_done

    @pyqtSlot()
    def update_button_text(self) -> None:
        text = 'Pre-Process File'
        if self.auto_process.isChecked():
            text += 's'

        self.process_file_button.setText(text)

    @pyqtSlot(list)
    def add_files(self, files: list[FileDetails]) -> None:
        self.status_list.add_files(files)

    @pyqtSlot(QTreeWidgetItem, QTreeWidgetItem)
    def selected_file_changed(self, current: FileStatusItem, prev: FileStatusItem) -> None:
        self.details.load_file(current.get_details().db_id)

    @pyqtSlot()
    def start_pre_processing(self) -> None:
        assert self._job_db_id is not None, 'Attempt to start pre-processing without a Job ID'
        self.reset_threads()

        selected_items = self.status_list.selectedItems()
        if not selected_items and not self.auto_process.isChecked():
            return

        if self.auto_process.isChecked():
            selected_items = [
                self.status_list.topLevelItem(idx) for idx in range(self.status_list.topLevelItemCount())
            ]

        self.process_file_button.setDisabled(True)
        for item in selected_items:
            if is_finished(item.get_status()):
                continue

            item.set_status(FileStatus.IN_PROGRESS)
            self.start_thread(item)

    #
    # THREAD CODE
    #

    def reset_threads(self) -> None:
        for thread, worker in self.pre_processing_threads.values():
            thread.quit()
            thread.wait()
        self.pre_processing_threads.clear()

    def threads_complete(self) -> None:
        if self.all_items_processed():
            self.process_file_button.setDisabled(False)
            self.process_file_button.setVisible(False)
            self.auto_process.setVisible(False)
            self.continue_button.setVisible(True)
        else:
            self.process_file_button.setDisabled(False)

    @pyqtSlot(int, FileStatus)
    def worker_status_update(self, db_id: int, status: FileStatus) -> None:
        for idx in range(self.status_list.topLevelItemCount()):
            item = self.status_list.topLevelItem(idx)

            # Update the status if this item matches the worker
            if item.get_details().db_id == db_id:
                item.set_status(status)

            # Update the details of this status matches the details
            if item.get_details().db_id == self.details.loaded_id():
                self.details.load_file(db_id)

    @pyqtSlot(int)
    def worker_complete(self, db_id: int) -> None:
        thread, _ = self.pre_processing_threads.pop(db_id)
        thread.quit()

        if not self.pre_processing_threads:
            self.threads_complete()

    def start_thread(self, item: FileStatusItem) -> None:
        thread = QThread(self)
        worker = PreProcessingWorker(self._job_db_id, item.get_details(), self.thread_mutex)
        worker.moveToThread(thread)

        worker.updateStatus.connect(self.worker_status_update)
        worker.processingComplete.connect(self.worker_complete)

        thread.started.connect(worker.start)
        thread.finished.connect(worker.deleteLater)

        thread.start()
        self.pre_processing_threads[item.get_details().db_id] = (thread, worker)
