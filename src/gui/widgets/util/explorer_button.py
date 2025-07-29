from pathlib import Path

from PyQt6.QtCore import QUrl
from PyQt6.QtGui import QDesktopServices
from PyQt6.QtWidgets import QPushButton, QWidget


class ExplorerButton(QPushButton):
    def __init__(self, path: Path, parent: QWidget | None = None):
        super().__init__('Open Directory', parent)
        self.path = path
        assert self.path.is_dir(), f'Path {self.path} is not a directory'

        self.pressed.connect(self._open_directory)

    def _open_directory(self) -> None:
        url = QUrl.fromLocalFile(str(self.path))
        QDesktopServices.openUrl(url)
