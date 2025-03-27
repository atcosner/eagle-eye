from PyQt6.QtCore import pyqtSlot
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QVBoxLayout, QListWidgetItem, QSplitter

from .file_dialog import ScanFileDialog
from .file_drop_list import FileDropList, FileItem
from .file_preview import FilePreview


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


class FilePicker(QWidget):
    def __init__(self):
        super().__init__()

        self.file_list = FileListWithButton()
        self.file_preview = FilePreview()
        self.file_list.file_list.currentItemChanged.connect(self.update_preview)

        self.splitter = QSplitter()
        self.splitter.addWidget(self.file_list)
        self.splitter.addWidget(self.file_preview)

        # When the splitter expands, just expand the preview
        self.splitter.setStretchFactor(0, 0)
        self.splitter.setStretchFactor(1, 1)

        layout = QHBoxLayout()
        layout.addWidget(self.splitter)
        self.setLayout(layout)

    @pyqtSlot(QListWidgetItem, QListWidgetItem)
    def update_preview(self, current: FileItem, _: FileItem):
        self.file_preview.update_preview(current.path())
