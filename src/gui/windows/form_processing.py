from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QMainWindow, QTabWidget

from ..widgets.file_picker import FilePicker

from .. import RESOURCES_PATH


class FormProcessing(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowIcon(QIcon(str(RESOURCES_PATH / 'white_icon.png')))

        self.picker = FilePicker()

        self.tabs = QTabWidget(self)
        self.tabs.addTab(self.picker, 'Step 1 - Choose Files')

        self.setCentralWidget(self.tabs)
