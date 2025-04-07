from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QMainWindow

from .. import RESOURCES_PATH


class BaseWindow(QMainWindow):
    def __init__(self, title_suffix: str | None = None):
        super().__init__()
        self.setWindowIcon(QIcon(str(RESOURCES_PATH / 'white_icon.png')))

        title = 'Eagle Eye'
        if title_suffix is not None:
            title += f' | {title_suffix}'
        self.setWindowTitle(title)
