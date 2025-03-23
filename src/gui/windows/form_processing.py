from PyQt6.QtWidgets import QMainWindow, QTabWidget

from ..widgets.file_picker import FilePicker


class FormProcessing(QMainWindow):
    def __init__(self):
        super().__init__()

        self.picker = FilePicker()

        self.tabs = QTabWidget(self)
        self.tabs.addTab(self.picker, 'Step 1 - Choose Files')

        self.setCentralWidget(self.tabs)
