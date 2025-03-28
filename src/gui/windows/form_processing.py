from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QMainWindow, QTabWidget

from ..tabs.file_picker import FilePicker
from ..tabs.file_pre_processing import FilePreProcessing

from .. import RESOURCES_PATH


class FormProcessing(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowIcon(QIcon(str(RESOURCES_PATH / 'white_icon.png')))
        self.setWindowTitle('Eagle Eye')

        self.picker = FilePicker()
        self.pre_processing = FilePreProcessing()

        self.tabs = QTabWidget(self)
        self.setCentralWidget(self.tabs)

        self.tabs.addTab(self.picker, 'Step 1 - Choose Files')
        self.tabs.addTab(self.pre_processing, 'Step 2 - Pre-Processing')

        self._connect_signals()

    def _connect_signals(self) -> None:
        self.picker.filesConfirmed.connect(self.pre_processing.add_files)
