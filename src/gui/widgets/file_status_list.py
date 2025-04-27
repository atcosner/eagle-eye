from PyQt6.QtCore import QSize
from PyQt6.QtGui import QIcon, QMovie
from PyQt6.QtWidgets import QTreeWidget, QTreeWidgetItem, QHeaderView, QLabel

from typing import Iterable

from numpy.version import git_revision

from src.util.resources import FILE_TYPE_ICON_PATH
from src.util.status import FileStatus, get_icon_for_status
from src.util.types import FileDetails

ICON_SIZE = QSize(40, 40)


class FileStatusItem(QTreeWidgetItem):
    def __init__(self, parent: QTreeWidget, file_details: FileDetails, initial_status: FileStatus):
        super().__init__(parent)
        self.details = file_details
        self.status: FileStatus = initial_status

        icon_file_name = 'pdf_icon.png' if self.details.path.suffix == '.pdf' else 'image_icon.png'
        self.setIcon(0, QIcon(str(FILE_TYPE_ICON_PATH / icon_file_name)))
        self.setText(1, self.details.path.name)
        self.set_status(self.status)

    def get_details(self) -> FileDetails:
        return self.details

    def set_status(self, status: FileStatus) -> None:
        self.status = status

        status_icon = get_icon_for_status(self.status)
        if isinstance(status_icon, QMovie):
            self.setIcon(2, QIcon())

            gif_label = QLabel()
            status_icon.setScaledSize(ICON_SIZE)
            gif_label.setMovie(status_icon)
            status_icon.start()

            self.treeWidget().setItemWidget(self, 2, gif_label)
        else:
            self.treeWidget().setItemWidget(self, 2, None)
            self.setIcon(2, status_icon)

    def get_status(self) -> FileStatus:
        return self.status


class FileStatusList(QTreeWidget):
    def __init__(self):
        super().__init__()
        self.setIconSize(ICON_SIZE)
        self.setHeaderLabels(('Type', 'Name', 'Status'))

        # Remove the implicit left-most column that shows the expand/collapse icon
        self.setRootIsDecorated(False)

        # Set column 1 (file name) to consume all extra space
        self.header().setStretchLastSection(False)
        self.header().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)

    def add_file(self, file: FileDetails, initial_status: FileStatus = FileStatus.PENDING) -> None:
        # Add to the top level through passing the tree widget into the constructor
        # - Allows us to call treeWidget() from the item later
        FileStatusItem(self, file, initial_status)

    def add_files(self, files: Iterable[FileDetails]) -> None:
        for file in files:
            self.add_file(file)
