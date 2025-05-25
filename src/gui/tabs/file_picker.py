import logging

from PyQt6.QtCore import pyqtSlot, pyqtSignal
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QVBoxLayout, QListWidgetItem, QSplitter

from src.database.job import Job
from src.util.types import FileDetails

from ..widgets.file.input_file_dialog import InputFileDialog
from ..widgets.file.file_drop_list import FileDropList, FileItem
from ..widgets.file_preview import FilePreview

logger = logging.getLogger(__name__)


class FileListWithButton(QWidget):
    def __init__(self):
        super().__init__()

        self._job_db_id: int | None = None

        self.file_list = FileDropList()

        self.add_files_button = QPushButton('Add files')
        self.add_files_button.pressed.connect(self.show_file_dialog)

        layout = QVBoxLayout()
        layout.addWidget(self.add_files_button)
        layout.addWidget(self.file_list)
        self.setLayout(layout)

    def set_view_only(self, view_only: bool) -> None:
        self.add_files_button.setVisible(not view_only)

    def load_job(self, job: Job | None) -> None:
        self._job_db_id = job.id if job else None
        self.file_list.load_job(job)

    @pyqtSlot()
    def show_file_dialog(self) -> None:
        dialog = InputFileDialog(self)
        if dialog.exec():
            self.file_list.add_items(dialog.selectedFiles())

    def get_files(self) -> list[FileDetails]:
        return self.file_list.get_files()


class FilePicker(QWidget):
    continueToNextStep = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setContentsMargins(0, 0, 0, 0)

        self._job_db_id: int | None = None

        self.file_list = FileListWithButton()
        self.file_preview = FilePreview()
        self.file_list.file_list.currentItemChanged.connect(self.update_preview)

        self.confirm_files_button = QPushButton('Confirm Files')
        self.confirm_files_button.pressed.connect(self.continueToNextStep)

        self.splitter = QSplitter()
        self.splitter.addWidget(self.file_list)
        self.splitter.addWidget(self.file_preview)

        # When the splitter expands, just expand the preview
        self.splitter.setStretchFactor(0, 0)
        self.splitter.setStretchFactor(1, 1)

        layout = QVBoxLayout()
        layout.addWidget(self.splitter)

        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(self.confirm_files_button)
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def set_view_only(self, view_only: bool) -> None:
        # Disable control functionality
        self.file_list.set_view_only(view_only)
        self.confirm_files_button.setVisible(not view_only)

    def load_job(self, job: Job | None) -> None:
        self._job_db_id = job.id if job else None
        self.file_list.load_job(job)

    @pyqtSlot(QListWidgetItem, QListWidgetItem)
    def update_preview(self, current: FileItem, _: FileItem):
        self.file_preview.update_preview(current.path())
