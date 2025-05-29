from PyQt6.QtCore import pyqtSlot
from sqlalchemy.orm import Session

from PyQt6.QtWidgets import QLineEdit, QVBoxLayout, QLabel, QHBoxLayout, QGroupBox, QRadioButton

from src.database import DB_ENGINE
from src.gui.widgets.reference_form.form_details_tree import FormDetailsTree

from .base import BasePage


class StartPage(BasePage):
    def __init__(self):
        super().__init__()
        self.setSubTitle('Specify a form name and determine the initial state')

        self.form_name = QLineEdit()

        self.options_box = QGroupBox()
        self.new_form_button = QRadioButton('Start with an empty form')
        self.existing_form_button = QRadioButton('Copy the settings and fields from an existing form')
        self.existing_forms = FormDetailsTree()

        self.new_form_button.toggled.connect(self.handle_radio_state_change)
        self.existing_form_button.toggled.connect(self.handle_radio_state_change)

        with Session(DB_ENGINE) as session:
            self.existing_forms.load_reference_forms(session)

        self._initial_state()
        self._set_up_layout()

    def _initial_state(self) -> None:
        self.new_form_button.setChecked(True)
        self.existing_form_button.setChecked(False)
        self.existing_forms.setDisabled(True)

    def _set_up_layout(self) -> None:
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel('Form Name:'))
        name_layout.addWidget(self.form_name)

        start_layout = QVBoxLayout()
        start_layout.addWidget(self.new_form_button)
        start_layout.addWidget(self.existing_form_button)
        start_layout.addWidget(self.existing_forms)
        self.options_box.setLayout(start_layout)

        layout = QVBoxLayout()
        layout.addWidget(QLabel('Welcome to the Reference Form creation wizard!'))
        layout.addWidget(QLabel('Please enter a name for the new form and choose to start fresh or from an existing form.'))
        layout.addSpacing(20)
        layout.addLayout(name_layout)
        layout.addSpacing(5)
        layout.addWidget(self.options_box)
        self.setLayout(layout)

    @pyqtSlot()
    def handle_radio_state_change(self) -> None:
        self.existing_forms.setDisabled(self.new_form_button.isChecked())
