import logging
from enum import Enum
from typing import Iterable

from PyQt6.QtCore import QSize
from PyQt6.QtGui import QIcon, QMovie
from PyQt6.QtWidgets import QTreeWidget, QTreeWidgetItem, QHeaderView, QLabel

from src.database import Job
from src.database.input_file import InputFile
from src.util.paths import is_pdf
from src.util.resources import FILE_TYPE_ICON_PATH
from src.util.status import FileStatus, get_icon_for_status
from src.util.types import FileDetails

ICON_SIZE = QSize(40, 40)

logger = logging.getLogger(__name__)


class ListMode(Enum):
    PRE_PROCESS = object()
    PROCESS = object()


class FileStatusItem(QTreeWidgetItem):
    def __init__(
            self,
            parent: QTreeWidget | QTreeWidgetItem,
            file: InputFile,
            initial_status: FileStatus,
    ):
        super().__init__(parent)
        self._db_id = file.id
        self.status: FileStatus = initial_status

        self.setExpanded(True)

        icon_file_name = 'pdf_icon.png' if is_pdf(file.path) else 'image_icon.png'
        self.setIcon(0, QIcon(str(FILE_TYPE_ICON_PATH / icon_file_name)))
        self.setText(1, file.path.name)
        self._set_own_status(self.status)

    def get_id(self) -> int:
        return self._db_id

    def _set_own_status(self, status: FileStatus):
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

    def set_status(self, db_id: int,  status: FileStatus) -> None:
        if db_id != self._db_id:
            for child_idx in range(self.childCount()):
                self.child(child_idx).set_status(db_id, status)

            # if we have children, our status is determined by theirs
            if self.childCount():
                child_statuses = [self.child(idx).get_status() for idx in range(self.childCount())]
                if any([(status == FileStatus.FAILED) for status in child_statuses]):
                    self._set_own_status(FileStatus.FAILED)
                elif all([(status == FileStatus.SUCCESS) for status in child_statuses]):
                    self._set_own_status(FileStatus.SUCCESS)
        else:
            self._set_own_status(status)

    def get_status(self) -> FileStatus:
        return self.status


class FileStatusList(QTreeWidget):
    def __init__(self):
        super().__init__()
        self._files_by_id: dict[int, FileStatusItem] = {}

        self.setIconSize(ICON_SIZE)
        self.setHeaderLabels(('Type', 'Name', 'Status'))

        # Set column 1 (file name) to consume all extra space
        self.header().setStretchLastSection(False)
        self.header().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)

    def add_file(self, file: FileDetails, initial_status: FileStatus = FileStatus.PENDING) -> None:
        # Add to the top level through passing the tree widget into the constructor
        # - Allows us to call treeWidget() from the item later
        item = FileStatusItem(self, file, initial_status)
        self._files_by_id[file.db_id] = item

    def add_files(self, files: Iterable[FileDetails]) -> None:
        for file in files:
            self.add_file(file)

    def load_job(self, mode: ListMode, job: Job) -> None:
        pending_files = []

        had_sub_items = False
        parent_item: QTreeWidget | QTreeWidgetItem = self
        for file in job.input_files:
            # nest files that are linked to other files
            if file.linked_input_file_id is not None:
                had_sub_items = True
                linked_file = self._files_by_id.get(file.linked_input_file_id, None)
                if linked_file is None:
                    logger.warning(f'{file.path.name}: linked file not found for ID {file.linked_input_file_id}')
                    pending_files.append(file)
                    continue

                logger.info(f'Nesting input file {file.id} under input file {file.linked_input_file_id}')
                parent_item = linked_file

            initial_status = FileStatus.PENDING
            if mode is ListMode.PRE_PROCESS:
                if file.pre_process_result is not None:
                    if file.pre_process_result.successful_alignment:
                        initial_status = FileStatus.SUCCESS
                    else:
                        initial_status = FileStatus.FAILED
            elif mode is ListMode.PROCESS:
                if not file.container_file:
                    # skip files that were not pre-processed
                    if file.pre_process_result is None:
                        continue

                    # skip files that were not aligned
                    if not file.pre_process_result.successful_alignment:
                        continue

                if file.process_result is not None:
                    initial_status = FileStatus.SUCCESS

            item = FileStatusItem(parent_item, file, initial_status)
            self._files_by_id[file.id] = item

        # TODO: process any remaining pending files

        # update the status for all top level items
        # TODO: this feels hacky
        for idx in range(self.topLevelItemCount()):
            self.topLevelItem(idx).set_status(-1, FileStatus.PENDING)

        # disable the top level items having an expand/collapse button if we had no sub-items
        self.setRootIsDecorated(had_sub_items)
