from PyQt6.QtCore import pyqtSlot
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QVBoxLayout, QListWidgetItem

from .file_dialog import ScanFileDialog
from .file_drop_list import FileDropList, FileItem
from .file_preview import FilePreview


class FilePicker(QWidget):
    def __init__(self):
        super().__init__()

        self.file_list = FileDropList()
        self.file_preview = FilePreview()
        self.file_list.currentItemChanged.connect(self.update_preview)

        self.add_files_button = QPushButton('Add files')
        self.add_files_button.pressed.connect(self.show_file_dialog)

        list_layout = QVBoxLayout()
        list_layout.addWidget(self.add_files_button)
        list_layout.addWidget(self.file_list)

        layout = QHBoxLayout()
        layout.addLayout(list_layout)
        layout.addWidget(self.file_preview)
        self.setLayout(layout)

    @pyqtSlot(QListWidgetItem, QListWidgetItem)
    def update_preview(self, current: FileItem, _: FileItem):
        self.file_preview.update_preview(current.path())

    @pyqtSlot()
    def show_file_dialog(self) -> None:
        dialog = ScanFileDialog(self)
        if dialog.exec():
            self.file_list.add_items(dialog.selectedFiles())
