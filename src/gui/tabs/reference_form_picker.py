import logging
from sqlalchemy.orm import Session

from PyQt6.QtCore import pyqtSignal, pyqtSlot, Qt
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QVBoxLayout, QSplitter, QMessageBox

from src.database import DB_ENGINE
from src.database.job import Job
from src.database.reference_form import ReferenceForm

from ..widgets.file_preview import FilePreview
from ..widgets.reference_form.form_details_tree import FormDetailsTree

logger = logging.getLogger(__name__)


class ReferenceFormPicker(QWidget):
    continueToNextStep = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setContentsMargins(0, 0, 0, 0)

        self._job_db_id: int | None = None

        self.form_tree = FormDetailsTree()
        self.form_tree.referenceFormChanged.connect(self.handle_reference_form_changed)

        self.file_preview = FilePreview()  # TODO: switch this to the view with fields painted on

        self.confirm_button = QPushButton('Confirm Reference Form')
        self.confirm_button.pressed.connect(self.continueToNextStep)
        self.confirm_button.setDisabled(True)

        self.splitter = QSplitter(Qt.Orientation.Vertical)
        self.splitter.addWidget(self.form_tree)
        self.splitter.addWidget(self.file_preview)

        # When the splitter expands, just expand the preview
        self.splitter.setStretchFactor(0, 0)
        self.splitter.setStretchFactor(1, 1)

        layout = QVBoxLayout()
        layout.addWidget(self.splitter)

        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(self.confirm_button)
        layout.addLayout(button_layout)

        self.setLayout(layout)
        self._load_reference_forms()

    def _load_reference_forms(self) -> None:
        with Session(DB_ENGINE) as session:
            self.form_tree.load_reference_forms(session)

    def set_view_only(self, view_only: bool) -> None:
        self.form_tree.setDisabled(view_only)
        self.confirm_button.setVisible(not view_only)

    def load_job(self, job: Job | None) -> None:
        self._job_db_id = job.id if job else None
        self.form_tree.set_reference_form(job.reference_form_id)
        self.set_view_only(False)

    def get_reference_form(self) -> int | None:
        return self.form_tree.get_reference_form()

    @pyqtSlot(int)
    def handle_reference_form_changed(self, db_id: int) -> None:
        with Session(DB_ENGINE) as session:
            reference_form = session.get(ReferenceForm, db_id)
            self.file_preview.update_preview(reference_form.path)

        self.confirm_button.setDisabled(False)
