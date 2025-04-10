from PyQt6.QtCore import pyqtSlot
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QCheckBox, QHBoxLayout

from pathlib import Path

from ..widgets.file_status_list import FileStatusList


class FilePreProcessing(QWidget):
    def __init__(self):
        super().__init__()

        self.status_list = FileStatusList()
        self.file_details = QWidget()

        self.process_file_button = QPushButton('Pre-Process Files')

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
