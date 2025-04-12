from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QMainWindow, QWidget

from ...util.resources import RESOURCES_PATH


class BaseWindow(QMainWindow):
    def __init__(self, parent: QWidget | None = None, title_suffix: str | None = None):
        super().__init__(parent)
        self.setWindowIcon(QIcon(str(RESOURCES_PATH / 'white_icon.png')))

        self.update_title(title_suffix)

    def update_title(self, suffix: str | None) -> None:
        base_title = 'Eagle Eye'
        if suffix is not None:
            base_title += f' | {suffix}'
        self.setWindowTitle(base_title)
