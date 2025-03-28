from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QTreeWidget, QTreeWidgetItem

from pathlib import Path
from typing import Iterable

from .. import RESOURCES_PATH


class FileStatusItem(QTreeWidgetItem):
    def __init__(self, file_path: Path):
        super().__init__()

        if file_path.suffix == '.pdf':
            self.setIcon(0, QIcon(str(RESOURCES_PATH / 'pdf_icon.png')))
        else:
            self.setIcon(0, QIcon(str(RESOURCES_PATH / 'image_icon.png')))

        self.setText(1, file_path.name)
        self.setIcon(2, QIcon(str(RESOURCES_PATH / 'file_pending.png')))

        self._path = file_path


class FileStatusList(QTreeWidget):
    def __init__(self):
        super().__init__()
        self.setColumnCount(3)
        self.setHeaderLabels(
            (
                'Type',
                'Name',
                'Status',
            )
        )

    def add_files(self, files: Iterable[Path]) -> None:
        self.addTopLevelItems([FileStatusItem(path) for path in files])
