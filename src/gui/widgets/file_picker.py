from PyQt6.QtWidgets import QWidget, QHBoxLayout

from .file_drop_list import FileDropList
from .file_preview import FilePreview


class FilePicker(QWidget):
    def __init__(self):
        super().__init__()

        self.file_list = FileDropList()
        self.file_preview = FilePreview()

        layout = QHBoxLayout()
        layout.addWidget(self.file_list)
        layout.addWidget(self.file_preview)
        self.setLayout(layout)
