from sqlalchemy.orm import Session

from PyQt6.QtCore import pyqtSlot
from PyQt6.QtWidgets import QLineEdit, QVBoxLayout, QLabel, QHBoxLayout, QPushButton, QFileDialog

from src.database import DB_ENGINE
from src.database.reference_form import ReferenceForm
from src.gui.widgets.file.input_file_dialog import InputFileDialog

from .base import BasePage


class FilePage(BasePage):
    def __init__(self):
        super().__init__()
        self.setSubTitle('What file will be used for the reference form?')

        self.file_path = QLineEdit()
        self.file_path.setReadOnly(True)
        self.registerField('form.file_path*', self.file_path)

        self.browse_button = QPushButton('Browse')
        self.browse_button.pressed.connect(self.show_file_dialog)

        self._set_up_layout()

    def _set_up_layout(self) -> None:
        path_layout = QHBoxLayout()
        path_layout.addWidget(self.file_path)
        path_layout.addWidget(self.browse_button)

        layout = QVBoxLayout()
        layout.addWidget(QLabel('Please select the reference form image'))
        layout.addSpacing(10)
        layout.addLayout(path_layout)
        layout.addStretch()
        self.setLayout(layout)

    @pyqtSlot()
    def show_file_dialog(self) -> None:
        dialog = InputFileDialog(self)
        dialog.setFileMode(QFileDialog.FileMode.ExistingFile)  # only a single file
        if dialog.exec():
            file = dialog.selectedFiles()[0]
            self.file_path.setText(file)

    #
    # Qt overrides
    #
    def initializePage(self) -> None:
        if self.field('form.copy_existing'):
            with Session(DB_ENGINE) as session:
                form = session.get(ReferenceForm, self.field('form.existing_id'))
                self.file_path.setText(str(form.path))
