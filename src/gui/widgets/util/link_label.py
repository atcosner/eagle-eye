from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QLabel


class LinkLabel(QLabel):
    def __init__(self, text: str):
        super().__init__(text)
        self.setTextFormat(Qt.TextFormat.RichText)
        self.setTextInteractionFlags(Qt.TextInteractionFlag.TextBrowserInteraction)
        self.setOpenExternalLinks(True)
