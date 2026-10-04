import logging
from sqlalchemy.orm import Session

from PyQt6.QtCore import pyqtSignal, pyqtSlot, Qt
from PyQt6.QtGui import QFont, QPalette, QColor
from PyQt6.QtWidgets import QFrame, QLabel, QLineEdit, QGridLayout, QPushButton, QHBoxLayout, QMessageBox

from src.database import DB_ENGINE
from src.database.input_file import InputFile

from .file_preview import FilePreview

logger = logging.getLogger(__name__)


class AlignmentCheckDetails(QFrame):
    alignmentConfirmed = pyqtSignal(int)
    alignmentRefineRequested = pyqtSignal(int)
    alignmentRejected = pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self.setFrameStyle(QFrame.Shape.Box)

        self._db_id: int | None = None
        self._view_only: bool = False
        self._refining_id: int | None = None

        self.file_name = QLineEdit()
        self.file_name.setDisabled(True)

        self.status_label = QLabel()
        status_font = QFont()
        status_font.setBold(True)
        self.status_label.setFont(status_font)
        self.status_label.setAutoFillBackground(True)
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        self.overlaid_viewer = FilePreview()

        self.confirm_button = QPushButton('Confirm Alignment')
        self.confirm_button.setVisible(False)
        self.confirm_button.pressed.connect(self.confirm_alignment)

        self.refine_button = QPushButton('Re-run Alignment')
        self.refine_button.setToolTip('Run another alignment pass on the aligned image to try to improve it')
        self.refine_button.setVisible(False)
        self.refine_button.pressed.connect(self.refine_alignment)

        self.reject_button = QPushButton('Reject Alignment')
        self.reject_button.setToolTip('Reject the alignment, this file will not be OCR\'d')
        self.reject_button.setVisible(False)
        self.reject_button.pressed.connect(self.reject_alignment)

        self._set_up_layout()

    def _set_up_layout(self) -> None:
        layout = QGridLayout()
        layout.addWidget(QLabel('File Name: '), 0, 0)
        layout.addWidget(self.file_name, 0, 1)

        layout.addWidget(QLabel('Status: '), 1, 0)
        layout.addWidget(self.status_label, 1, 1)

        layout.addWidget(self.overlaid_viewer, 2, 0, 1, 2)
        layout.setRowStretch(2, 1)

        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(self.reject_button)
        button_layout.addWidget(self.refine_button)
        button_layout.addWidget(self.confirm_button)
        layout.addLayout(button_layout, 3, 0, 1, 2)

        self.setLayout(layout)

    def _set_status(self, text: str, color: str | None) -> None:
        palette = QPalette()
        if color is not None:
            palette.setColor(QPalette.ColorRole.WindowText, QColor('black'))
            palette.setColor(QPalette.ColorRole.Window, QColor(color))

        self.status_label.setText(text)
        self.status_label.setPalette(palette)

    def reset(self) -> None:
        self.hide()
        self._db_id = None

    def set_view_only(self, view_only: bool) -> None:
        self._view_only = view_only
        if self._db_id is not None:
            self.load_file(self._db_id)

    def set_refining(self, db_id: int | None) -> None:
        # Only allow one re-alignment at a time
        self._refining_id = db_id
        self.confirm_button.setDisabled(db_id is not None)
        self.refine_button.setDisabled(db_id is not None)
        self.reject_button.setDisabled(db_id is not None)
        if self._db_id is not None:
            self.load_file(self._db_id)

    def loaded_id(self) -> int | None:
        return self._db_id

    def load_file(self, db_id: int) -> None:
        self._db_id = db_id
        self.confirm_button.setVisible(False)
        self.refine_button.setVisible(False)
        self.reject_button.setVisible(False)

        with Session(DB_ENGINE) as session:
            file = session.get(InputFile, db_id)
            if file is None:
                logger.error(f'No input file found for ID: {db_id}')
                return

            # remove ourselves from view on container items
            if file.container_file:
                self.hide()
                return
            else:
                self.show()

            self.file_name.setText(file.path.name)

            result = file.pre_process_result
            if result is None or not result.alignment_possible or result.overlaid_image_path is None:
                self._set_status('ALIGNMENT FAILED (Will not be processed)', 'red')
                self.overlaid_viewer.clear()
                return

            self.overlaid_viewer.update_preview(result.overlaid_image_path)

            # Files that were OCR'd can no longer be changed
            if file.process_result is not None:
                self._set_status('CONFIRMED', 'green')
                return

            self.refine_button.setVisible(not self._view_only)
            self.reject_button.setVisible(not self._view_only)

            if db_id == self._refining_id:
                self._set_status('RE-RUNNING ALIGNMENT...', None)
            elif result.alignment_confirmed:
                self._set_status('CONFIRMED', 'green')
            else:
                if result.fully_aligned:
                    self._set_status('PENDING CONFIRMATION', None)
                else:
                    self._set_status('PENDING CONFIRMATION (Partial Alignment)', 'yellow')
                self.confirm_button.setVisible(not self._view_only)

    @pyqtSlot()
    def confirm_alignment(self) -> None:
        if self._db_id is not None:
            with Session(DB_ENGINE) as session:
                file = session.get(InputFile, self._db_id)
                file.pre_process_result.alignment_confirmed = True
                session.commit()

            self.alignmentConfirmed.emit(self._db_id)
        else:
            logger.warning('Attempted to confirm alignment but did not have a DB ID')

    @pyqtSlot()
    def reject_alignment(self) -> None:
        if self._db_id is None:
            logger.warning('Attempted to reject alignment but did not have a DB ID')
            return

        answer = QMessageBox.question(
            self,
            'Reject Alignment',
            'Reject this alignment? The file will not be OCR\'d and this cannot be undone.',
        )
        if answer != QMessageBox.StandardButton.Yes:
            return

        # Rejected files are treated the same as files that could not be aligned
        with Session(DB_ENGINE) as session:
            file = session.get(InputFile, self._db_id)
            file.pre_process_result.alignment_possible = False
            file.pre_process_result.alignment_confirmed = False
            session.commit()

        self.alignmentRejected.emit(self._db_id)
        self.load_file(self._db_id)

    @pyqtSlot()
    def refine_alignment(self) -> None:
        if self._db_id is not None:
            self.alignmentRefineRequested.emit(self._db_id)
        else:
            logger.warning('Attempted to refine alignment but did not have a DB ID')
