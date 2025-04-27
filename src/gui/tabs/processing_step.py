from typing import Type

from PyQt6.QtCore import pyqtSlot, QThread, QMutex, pyqtSignal, QObject
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QCheckBox, QHBoxLayout, QTreeWidgetItem

from src.database.job import Job
from src.util.status import FileStatus, is_finished

from src.gui.widgets.file.file_status_list import FileStatusList, FileStatusItem


class ProcessingStep(QWidget):
    continueToNextStep = pyqtSignal()

    def __init__(self, step_button_text: str, details_cls: Type[QWidget] | None):
        super().__init__()
        self._job_db_id: int | None = None
        self._step_button_text = step_button_text

        self.thread_idx: int = 0
        self.thread_mutex: QMutex = QMutex()
        self.threads: dict[int, tuple[QThread, QObject]] = {}

        self.file_list = FileStatusList()
        self.file_list.currentItemChanged.connect(self.selected_file_changed)

        self.step_details: QWidget | None = details_cls() if details_cls is not None else None

        self.process_file_button = QPushButton(step_button_text)
        self.process_file_button.pressed.connect(self.start_processing)

        self.auto_process = QCheckBox('Process All')
        self.auto_process.setChecked(True)
        self.auto_process.checkStateChanged.connect(self.update_button_text)

        self.continue_button = QPushButton('Continue')
        self.continue_button.pressed.connect(self.continueToNextStep)

        self._initial_state()
        self._set_up_layout()

    def _initial_state(self) -> None:
        # Disable the processing controls
        self.process_file_button.setDisabled(True)
        self.auto_process.setDisabled(True)

        # Hide the next step button
        self.continue_button.setVisible(False)

    def _set_up_layout(self) -> None:
        layout = QVBoxLayout()
        layout.addWidget(self.file_list)
        layout.addWidget(self.step_details)

        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(self.auto_process)
        button_layout.addWidget(self.process_file_button)
        button_layout.addWidget(self.continue_button)
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def set_view_only(self, view_only: bool) -> None:
        # Hide control functionality
        self.auto_process.setVisible(not view_only)
        self.process_file_button.setVisible(not view_only)
        self.continue_button.setVisible(not view_only)

    def update_control_state(self) -> None:
        # Check if we have no files
        if not self.file_list.topLevelItemCount():
            self._initial_state()

        # Check if all items have been processed
        elif self.all_items_processed():
            self.auto_process.setVisible(False)
            self.process_file_button.setVisible(False)
            self.continue_button.setVisible(True)

        # Files still need processing
        else:
            self.auto_process.setVisible(True)
            self.auto_process.setDisabled(False)
            self.process_file_button.setVisible(True)
            self.process_file_button.setDisabled(False)

    def load_job(self, job: Job | int | None) -> None:
        self.file_list.clear()
        # TODO: Clear details
        self._job_db_id = None if job is None else job.id if isinstance(job, Job) else job

    def all_items_processed(self) -> bool:
        # Don't consider all processing done if we have no files
        if not self.file_list.topLevelItemCount():
            return False

        all_done = True
        for idx in range(self.file_list.topLevelItemCount()):
            item = self.file_list.topLevelItem(idx)
            if not is_finished(item.get_status()):
                all_done = False

        return all_done

    @pyqtSlot()
    def update_button_text(self) -> None:
        text = self._step_button_text
        if self.auto_process.isChecked():
            text += 's'

        self.process_file_button.setText(text)

    @pyqtSlot(QTreeWidgetItem, QTreeWidgetItem)
    def selected_file_changed(self, current: FileStatusItem, _: FileStatusItem) -> None:
        if self.step_details is not None:
            self.step_details.load_file(current.get_details().db_id)

    @pyqtSlot()
    def start_processing(self) -> None:
        assert self._job_db_id is not None, 'Attempt to start pre-processing without a Job ID'
        self.reset_threads()

        if not self.file_list.topLevelItemCount():
            return

        selected_items = self.file_list.selectedItems()
        if not selected_items and not self.auto_process.isChecked():
            return

        if self.auto_process.isChecked():
            selected_items = [
                self.file_list.topLevelItem(idx) for idx in range(self.file_list.topLevelItemCount())
            ]

        self.process_file_button.setDisabled(True)
        for item in selected_items:
            if is_finished(item.get_status()):
                continue

            item.set_status(FileStatus.IN_PROGRESS)
            self.start_worker(item)

    #
    # THREAD CODE
    #

    def reset_threads(self) -> None:
        for thread, worker in self.threads.values():
            thread.quit()
            thread.wait()
        self.threads.clear()

    @pyqtSlot(int, FileStatus)
    def worker_status_update(self, db_id: int, status: FileStatus) -> None:
        for idx in range(self.file_list.topLevelItemCount()):
            item = self.file_list.topLevelItem(idx)

            # Update the status if this item matches the worker
            if item.get_details().db_id == db_id:
                item.set_status(status)

            # Update the details of this status matches the details
            if self.step_details is not None and item.get_details().db_id == self.step_details.loaded_id():
                self.step_details.load_file(db_id)

    @pyqtSlot(int)
    def worker_complete(self, db_id: int) -> None:
        thread, _ = self.threads.pop(db_id)
        thread.quit()

        if not self.threads:
            self.update_control_state()

    def start_thread(self, item: FileStatusItem, worker: QWidget) -> None:
        thread = QThread(self)
        worker.moveToThread(thread)

        thread.started.connect(worker.start)
        thread.finished.connect(worker.deleteLater)

        thread.start()
        self.threads[item.get_details().db_id] = (thread, worker)
