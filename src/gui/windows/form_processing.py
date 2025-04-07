from PyQt6.QtWidgets import QTabWidget

from .base import BaseWindow
from ..tabs.file_picker import FilePicker
from ..tabs.file_pre_processing import FilePreProcessing


class FormProcessing(BaseWindow):
    def __init__(self):
        super().__init__('Form Processing')

        self.picker = FilePicker()
        self.pre_processing = FilePreProcessing()

        self.tabs = QTabWidget(self)
        self.setCentralWidget(self.tabs)

        self.tabs.addTab(self.picker, 'Step 1 - Choose Files')
        self.tabs.addTab(self.pre_processing, 'Step 2 - Pre-Processing')

        self._connect_signals()

    def _connect_signals(self) -> None:
        self.picker.filesConfirmed.connect(self.pre_processing.add_files)
