from PyQt6.QtCore import pyqtSlot
from PyQt6.QtWidgets import QWidget, QVBoxLayout

from pathlib import Path

from ..widgets.file_status_list import FileStatusList


class FilePreProcessing(QWidget):
    def __init__(self):
        super().__init__()

        self.status_list = FileStatusList()

        layout = QVBoxLayout()
        layout.addWidget(self.status_list)
        self.setLayout(layout)

    @pyqtSlot(list)
    def add_files(self, files: list[Path]) -> None:
        self.status_list.add_files(files)
