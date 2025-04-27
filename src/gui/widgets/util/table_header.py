from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QLabel


class TableHeader(QLabel):
    def __init__(self, text: str):
        super().__init__(text)

        font = QFont()
        font.setPointSize(int(font.pointSize() * 1.25))
        font.setBold(True)
        self.setFont(font)
