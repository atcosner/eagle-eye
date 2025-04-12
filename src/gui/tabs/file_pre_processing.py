from PyQt6.QtCore import pyqtSlot, QThread, QMutex
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QCheckBox, QHBoxLayout, QTreeWidgetItem

from src.database.job import Job
from src.processing.pre_process_worker import PreProcessingWorker
from src.util.status import FileStatus, is_finished
from src.util.types import InputFileDetails

from ..widgets.file_status_list import FileStatusList, FileStatusItem
from ..windows.pre_processing_result import PreProcessingResult


class FilePreProcessing(QWidget):
    def __init__(self):
        super().__init__()
        self._job_db_id: int | None = None

        self.thread_idx: int = 0
        self.thread_mutex: QMutex = QMutex()
        self.pre_processing_threads: dict[int, tuple[QThread, PreProcessingWorker]] = {}

        self.status_list = FileStatusList()
        self.status_list.fileClicked.connect(self.file_clicked)

        self.process_file_button = QPushButton('Pre-Process Files')
        self.process_file_button.pressed.connect(self.start_pre_processing)

        self.auto_process = QCheckBox('Process All')
        self.auto_process.setChecked(True)
        self.auto_process.checkStateChanged.connect(self.update_button_text)

        self._set_layout()

    def _set_layout(self) -> None:
        layout = QVBoxLayout()
        layout.addWidget(self.status_list)

        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(self.auto_process)
        button_layout.addWidget(self.process_file_button)
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def load_job(self, job: Job | None) -> None:
        self._job_db_id = job.id if job else None

    def reset_threads(self) -> None:
        for thread, worker in self.pre_processing_threads.values():
            thread.quit()
            thread.wait()
        self.pre_processing_threads.clear()

    @pyqtSlot()
    def update_button_text(self) -> None:
        text = 'Pre-Process File'
        if self.auto_process.isChecked():
            text += 's'

        self.process_file_button.setText(text)

    @pyqtSlot(list)
    def add_files(self, files: list[InputFileDetails]) -> None:
        self.status_list.add_files(files)

    @pyqtSlot(QTreeWidgetItem, int)
    def file_clicked(self, item: FileStatusItem, col: int) -> None:
        if not is_finished(item.get_status()):
            return

        window = PreProcessingResult(self, item.get_details().db_id)
        window.show()

    @pyqtSlot(int, FileStatus)
    def worker_status_update(self, db_id: int, status: FileStatus) -> None:
        for idx in range(self.status_list.topLevelItemCount()):
            item = self.status_list.topLevelItem(idx)

            if item.get_details().db_id == db_id:
                item.set_status(status)
                return

    @pyqtSlot(int)
    def worker_complete(self, db_id: int) -> None:
        thread, _ = self.pre_processing_threads.pop(db_id)
        thread.quit()

        if not self.pre_processing_threads:
            self.process_file_button.setDisabled(False)

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
