from PyQt6.QtCore import pyqtSlot, pyqtSignal
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QVBoxLayout, QListWidgetItem, QSplitter

from pathlib import Path

from ..widgets.file_dialog import ScanFileDialog
from ..widgets.file_drop_list import FileDropList, FileItem
from ..widgets.file_preview import FilePreview


class FileListWithButton(QWidget):
    def __init__(self):
        super().__init__()

        self.file_list = FileDropList()

        self.add_files_button = QPushButton('Add files')
        self.add_files_button.pressed.connect(self.show_file_dialog)

        layout = QVBoxLayout()
        layout.addWidget(self.add_files_button)
        layout.addWidget(self.file_list)
        self.setLayout(layout)

    @pyqtSlot()
    def show_file_dialog(self) -> None:
        dialog = ScanFileDialog(self)
        if dialog.exec():
            self.file_list.add_items(dialog.selectedFiles())

    def get_files(self) -> list[Path]:
        return self.file_list.get_files()


class FilePicker(QWidget):
    filesConfirmed = pyqtSignal(list)  # list[Path]

    def __init__(self):
        super().__init__()
        self.setContentsMargins(0, 0, 0, 0)

        self.file_list = FileListWithButton()
        self.file_preview = FilePreview()
        self.file_list.file_list.currentItemChanged.connect(self.update_preview)

        self.confirm_files_button = QPushButton('Confirm Files')
        self.confirm_files_button.pressed.connect(self.confirm_files)

        self.splitter = QSplitter()
        self.splitter.addWidget(self.file_list)
        self.splitter.addWidget(self.file_preview)

        # When the splitter expands, just expand the preview
        self.splitter.setStretchFactor(0, 0)
        self.splitter.setStretchFactor(1, 1)

        layout = QVBoxLayout()
        layout.addWidget(self.splitter)

        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(self.confirm_files_button)
        layout.addLayout(button_layout)

        self.setLayout(layout)

    @pyqtSlot(QListWidgetItem, QListWidgetItem)
    def update_preview(self, current: FileItem, _: FileItem):
        self.file_preview.update_preview(current.path())

    @pyqtSlot()
    def confirm_files(self) -> None:
        files = self.file_list.get_files()
        print(files)
        self.filesConfirmed.emit(files)
