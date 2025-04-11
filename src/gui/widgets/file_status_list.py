from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon, QMovie
from PyQt6.QtWidgets import QTreeWidget, QTreeWidgetItem, QHeaderView

from pathlib import Path
from typing import Iterable

from ...util.resources import RESOURCES_PATH
from ...util.status import FileStatus, get_icon_for_status


class FileStatusItem(QTreeWidgetItem):
    def __init__(self, file_path: Path):
        super().__init__()
        self.path = file_path
        self.status: FileStatus = FileStatus.PENDING

        icon_file_name = 'pdf_icon.png' if file_path.suffix == '.pdf' else 'image_icon.png'
        self.setIcon(0, QIcon(str(RESOURCES_PATH / icon_file_name)))
        self.setText(1, file_path.name)
        self.set_status(self.status)

        self._path = file_path

    def set_status(self, status: FileStatus) -> None:
        self.status = status

        status_icon = get_icon_for_status(self.status)
        if isinstance(status_icon, QMovie):
            pass
        else:
            self.setIcon(2, status_icon)

    def get_status(self) -> FileStatus:
        return self.status


class FileStatusList(QTreeWidget):
    def __init__(self):
        super().__init__()
        self.setIconSize(QSize(40, 40))
        self.setHeaderLabels(('Type', 'Name', 'Status'))

        # Remove the implicit left-most column that shows the expand/collapse icon
        self.setRootIsDecorated(False)

        # Set column 1 (file name) to consume all extra space
        self.header().setStretchLastSection(False)
        self.header().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)

    def add_files(self, files: Iterable[Path]) -> None:
        self.addTopLevelItems([FileStatusItem(path) for path in files])
