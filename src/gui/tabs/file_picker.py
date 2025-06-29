import logging

from PyQt6.QtCore import pyqtSlot, pyqtSignal
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QVBoxLayout, QSplitter, QMessageBox

from src.database.job import Job
from src.util.types import FileDetails

from ..widgets.file.input_file_dialog import InputFileDialog
from ..widgets.file.file_drop_list import FileDropList
from ..widgets.file_preview import FilePreview

logger = logging.getLogger(__name__)


class FileListWithButton(QWidget):
    clearPreview = pyqtSignal()

    def __init__(self):
        super().__init__()
        self._job_db_id: int | None = None

        self.file_list = FileDropList()
        self.file_list.itemSelectionChanged.connect(self.handle_selection_change)

        self.add_files_button = QPushButton('Add')
        self.add_files_button.pressed.connect(self.show_file_dialog)

        self.remove_file_button = QPushButton('Remove')
        self.remove_file_button.setVisible(False)
        self.remove_file_button.pressed.connect(self.remove_file)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.add_files_button)
        button_layout.addStretch()
        button_layout.addWidget(self.remove_file_button)

        layout = QVBoxLayout()
        layout.addLayout(button_layout)
        layout.addWidget(self.file_list)
        self.setLayout(layout)

    def set_view_only(self, view_only: bool) -> None:
        self.add_files_button.setVisible(not view_only)
        self.remove_file_button.setVisible(not view_only)

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

    @pyqtSlot()
    def remove_file(self) -> None:
        # clear the preview as we can't delete PDFs that are open in the preview
        self.clearPreview.emit()
        self.file_list.remove_selected_item()

    @pyqtSlot()
    def handle_selection_change(self) -> None:
        self.remove_file_button.setVisible(bool(self.file_list.selectedItems()))


class FilePicker(QWidget):
    continueToNextStep = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setContentsMargins(0, 0, 0, 0)

        self._job_db_id: int | None = None

        self.file_list = FileListWithButton()
        self.file_preview = FilePreview()

        self.file_list.file_list.itemSelectionChanged.connect(self.update_preview)
        self.file_list.clearPreview.connect(self.file_preview.clear)

        self.confirm_files_button = QPushButton('Confirm Files')
        self.confirm_files_button.pressed.connect(self.check_continue)

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

    @pyqtSlot()
    def update_preview(self) -> None:
        selected_items = self.file_list.file_list.selectedItems()
        if selected_items:
            self.file_preview.update_preview(selected_items[0].path())
        else:
            self.file_preview.clear()

    @pyqtSlot()
    def check_continue(self) -> None:
        if not self.file_list.get_files():
            QMessageBox.critical(self, 'Error', 'Please select input files before continuing')
        else:
            self.continueToNextStep.emit()
