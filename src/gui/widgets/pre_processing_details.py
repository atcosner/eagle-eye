import logging
from sqlalchemy.orm import Session

from PyQt6.QtCore import pyqtSlot, Qt
from PyQt6.QtGui import QFont, QPalette, QColor
from PyQt6.QtWidgets import QFrame, QLabel, QLineEdit, QGridLayout, QPushButton

from src.database import DB_ENGINE
from src.database.input_file import InputFile

from ..windows.pre_processing_result import PreProcessingResult

logger = logging.getLogger(__name__)


class PreProcessingDetails(QFrame):
    def __init__(self):
        super().__init__()
        self.setFrameStyle(QFrame.Shape.Box)

        self._db_id: int | None = None

        self.file_name = QLineEdit()
        self.file_name.setDisabled(True)

        self.file_path = QLineEdit()
        self.file_path.setDisabled(True)

        self.status_label = QLabel()
        self.status_font = QFont()
        self.status_font.setBold(True)
        self.status_label.setFont(self.status_font)
        self.status_label.setAutoFillBackground(True)
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        self.accepted_rotation_label = QLabel()
        rotation_font = QFont()
        rotation_font.setBold(True)
        self.accepted_rotation_label.setFont(rotation_font)

        self.view_result_button = QPushButton('View Results')
        self.view_result_button.setVisible(False)
        self.view_result_button.pressed.connect(self.view_results)

        self._set_up_layout()

    def _set_up_layout(self) -> None:
        layout = QGridLayout()
        layout.addWidget(QLabel('File Name: '), 0, 0)
        layout.addWidget(self.file_name, 0, 1)

        layout.addWidget(QLabel('File Path: '), 1, 0)
        layout.addWidget(self.file_path, 1, 1)

        layout.addWidget(QLabel('Status: '), 2, 0)
        layout.addWidget(self.status_label, 2, 1)

        layout.addWidget(QLabel('Accepted Rotation Angle: '), 3, 0)
        layout.addWidget(self.accepted_rotation_label, 3, 1)

        layout.addWidget(self.view_result_button, 4, 0)

        self.setLayout(layout)

    def loaded_id(self) -> int | None:
        return self._db_id

    def load_file(self, db_id: int) -> None:
        self._db_id = db_id

        with Session(DB_ENGINE) as session:
            file = session.get(InputFile, db_id)
            if file is None:
                logger.error(f'No input file found for ID: {db_id}')
                self.view_result_button.setVisible(False)
                return

            self.status_label.setText('PENDING')
            self.accepted_rotation_label.setText('None')

            self.file_name.setText(file.path.name)
            self.file_path.setText(str(file.path))

            if file.pre_process_result is not None:
                palette = QPalette()
                if file.pre_process_result.successful_alignment:
                    self.status_label.setText('SUCCESS')
                    palette.setColor(QPalette.ColorRole.Window, QColor('green'))
                else:
                    self.status_label.setText('FAILED')
                    palette.setColor(QPalette.ColorRole.Window, QColor('red'))
                self.status_label.setPalette(palette)

                angle_str = f'{file.pre_process_result.accepted_rotation_angle} degrees'
                self.accepted_rotation_label.setText(angle_str)
                self.view_result_button.setVisible(True)

    @pyqtSlot()
    def view_results(self) -> None:
        window = PreProcessingResult(self, self._db_id)
        window.show()
