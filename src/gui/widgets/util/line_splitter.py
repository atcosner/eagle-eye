from PyQt6.QtWidgets import QSplitter


class LineSplitter(QSplitter):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("QSplitter::handle { background-color: lightgray; }")
