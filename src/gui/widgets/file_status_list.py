from PyQt6.QtCore import QSize, pyqtSignal
from PyQt6.QtGui import QIcon, QMovie
from PyQt6.QtWidgets import QTreeWidget, QTreeWidgetItem, QHeaderView

from typing import Iterable

from src.util.resources import RESOURCES_PATH
from src.util.status import FileStatus, get_icon_for_status
from src.util.types import FileDetails


class FileStatusItem(QTreeWidgetItem):
    def __init__(self, file_details: FileDetails):
        super().__init__()
        self.details = file_details
        self.status: FileStatus = FileStatus.PENDING

        icon_file_name = 'pdf_icon.png' if self.details.path.suffix == '.pdf' else 'image_icon.png'
        self.setIcon(0, QIcon(str(RESOURCES_PATH / icon_file_name)))
        self.setText(1, self.details.path.name)
        self.set_status(self.status)

    def get_details(self) -> FileDetails:
        return self.details

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

    def add_file(self, file: FileDetails) -> None:
        self.addTopLevelItem(FileStatusItem(file))

    def add_files(self, files: Iterable[FileDetails]) -> None:
        for file in files:
            self.add_file(file)
