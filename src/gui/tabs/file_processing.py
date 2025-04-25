from sqlalchemy.orm import Session

from PyQt6.QtCore import pyqtSlot, QMutex, QThread
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QCheckBox, QPushButton, QHBoxLayout

from src.database import DB_ENGINE
from src.database.job import Job
from src.processing.process_worker import ProcessWorker
from src.util.resources import GENERIC_ICON_PATH
from src.util.settings import SettingsManager
from src.util.status import FileStatus, is_finished
from src.util.types import FileDetails

from ..widgets.file_status_list import FileStatusList, FileStatusItem


class FileProcessing(QWidget):
    def __init__(self):
        super().__init__()
        self._job_db_id: int | None = None

        self.thread_idx: int = 0
        self.thread_mutex: QMutex = QMutex()
        self.threads: dict[int, tuple[QThread, ProcessWorker]] = {}

        self.status_list = FileStatusList()
        # self.status_list.currentItemChanged.connect(self.selected_file_changed)

        self.auto_process = QCheckBox('Process All')
        self.auto_process.setChecked(True)
        self.auto_process.checkStateChanged.connect(self.update_button_text)

        self.process_file_button = QPushButton('Process Files')
        self.process_file_button.pressed.connect(self.start_processing)

        self.view_results_button = QPushButton('View Results')
        self.view_results_button.setVisible(False)

        self._set_up_layout()
        self._check_api_config()

    def all_items_processed(self) -> bool:
        all_done = True
        for idx in range(self.status_list.topLevelItemCount()):
            item = self.status_list.topLevelItem(idx)
            if not is_finished(item.get_status()):
                all_done = False

        return all_done

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

    def load_job(self, job: Job | int | None) -> None:
        self.status_list.clear()
        if job is None:
            self._job_db_id = None
            return

        with Session(DB_ENGINE) as session:
            job = session.get(Job, job) if isinstance(job, int) else job
            self._job_db_id = job.id

            for input_file in job.input_files:
                # Only add files that have been pre-processed successfully
                if input_file.pre_process_result is None:
                    continue

                # Only add files that were aligned to their reference
                if not input_file.pre_process_result.successful_alignment:
                    continue

                self.status_list.add_file(
                    file=FileDetails(
                        db_id=input_file.id,
                        path=input_file.path,
                    ),
                    # TODO: Failed status?
                    initial_status=FileStatus.SUCCESS if input_file.process_result is not None else FileStatus.PENDING,
                )

        # Run GUI updates based if all our items are complete
        self.threads_complete()

    @pyqtSlot()
    def start_processing(self) -> None:
        assert self._job_db_id is not None, 'Attempt to start processing without a Job ID'
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
        for thread, worker in self.threads.values():
            thread.quit()
            thread.wait()
        self.threads.clear()

    def threads_complete(self) -> None:
        if self.all_items_processed():
            self.process_file_button.setDisabled(False)
            self.process_file_button.setVisible(False)
            self.auto_process.setVisible(False)
            self.view_results_button.setVisible(True)
        else:
            self.process_file_button.setDisabled(False)

    @pyqtSlot(int, FileStatus)
    def worker_status_update(self, db_id: int, status: FileStatus) -> None:
        for idx in range(self.status_list.topLevelItemCount()):
            item = self.status_list.topLevelItem(idx)

            # Update the status if this item matches the worker
            if item.get_details().db_id == db_id:
                item.set_status(status)

            # # Update the details of this status matches the details
            # if item.get_details().db_id == self.details.loaded_id():
            #     self.details.load_file(db_id)

    @pyqtSlot(int)
    def worker_complete(self, db_id: int) -> None:
        thread, _ = self.threads.pop(db_id)
        thread.quit()

        if not self.threads:
            self.threads_complete()

    def start_thread(self, item: FileStatusItem) -> None:
        details = item.get_details()

        thread = QThread(self)
        worker = ProcessWorker(details.path.name, self._job_db_id, details.db_id, self.thread_mutex)
        worker.moveToThread(thread)

        worker.updateStatus.connect(self.worker_status_update)
        worker.processComplete.connect(self.worker_complete)

        thread.started.connect(worker.start)
        thread.finished.connect(worker.deleteLater)

        thread.start()
        self.threads[item.get_details().db_id] = (thread, worker)
