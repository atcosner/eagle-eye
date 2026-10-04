import logging
from sqlalchemy.orm import Session

from PyQt6.QtCore import pyqtSignal, pyqtSlot, Qt
from PyQt6.QtGui import QFont, QPalette, QColor
from PyQt6.QtWidgets import QFrame, QLabel, QLineEdit, QGridLayout, QPushButton

from src.database import DB_ENGINE
from src.database.input_file import InputFile

from .file_preview import FilePreview

logger = logging.getLogger(__name__)


class AlignmentCheckDetails(QFrame):
    alignmentConfirmed = pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self.setFrameStyle(QFrame.Shape.Box)

        self._db_id: int | None = None
        self._view_only: bool = False
        self._confirmed_ids: set[int] = set()

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

        self._set_up_layout()

    def _set_up_layout(self) -> None:
        layout = QGridLayout()
        layout.addWidget(QLabel('File Name: '), 0, 0)
        layout.addWidget(self.file_name, 0, 1)

        layout.addWidget(QLabel('Status: '), 1, 0)
        layout.addWidget(self.status_label, 1, 1)

        layout.addWidget(self.overlaid_viewer, 2, 0, 1, 2)
        layout.setRowStretch(2, 1)

        layout.addWidget(self.confirm_button, 3, 1, Qt.AlignmentFlag.AlignRight)

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

    def clear_confirmations(self) -> None:
        self._confirmed_ids.clear()

    def set_view_only(self, view_only: bool) -> None:
        self._view_only = view_only
        if self._db_id is not None:
            self.load_file(self._db_id)

    def loaded_id(self) -> int | None:
        return self._db_id

    def load_file(self, db_id: int) -> None:
        self._db_id = db_id
        self.confirm_button.setVisible(False)

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

            # Files that were OCR'd had their alignment confirmed previously
            if db_id in self._confirmed_ids or file.process_result is not None:
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
            self._confirmed_ids.add(self._db_id)
            self.alignmentConfirmed.emit(self._db_id)
        else:
            logger.warning('Attempted to confirm alignment but did not have a DB ID')
