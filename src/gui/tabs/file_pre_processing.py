from pathlib import Path

from PyQt6.QtCore import pyqtSlot, QThread
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QCheckBox, QHBoxLayout

from src.processing.pre_process_worker import PreProcessingWorker
from src.util.status import FileStatus, is_finished

from ..widgets.file_status_list import FileStatusList, FileStatusItem


class FilePreProcessing(QWidget):
    def __init__(self):
        super().__init__()
        self.pre_processing_threads: list[QThread] = []

        self.status_list = FileStatusList()
        self.file_details = QWidget()

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

    @pyqtSlot()
    def update_button_text(self) -> None:
        text = 'Pre-Process File'
        if self.auto_process.isChecked():
            text += 's'

        self.process_file_button.setText(text)

    @pyqtSlot(list)
    def add_files(self, files: list[Path]) -> None:
        self.status_list.add_files(files)

    def start_thread(self, item: FileStatusItem) -> None:
        thread = QThread(self)
        worker = PreProcessingWorker(item.path)
        worker.moveToThread(thread)

        thread.started.connect(worker.start)
        thread.finished.connect(worker.deleteLater)

        thread.start()
        self.pre_processing_threads.append((thread, worker))

    @pyqtSlot()
    def start_pre_processing(self) -> None:
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
