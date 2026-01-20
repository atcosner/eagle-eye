from sqlalchemy.orm import Session

from PyQt6.QtCore import pyqtSlot, Qt
from PyQt6.QtWidgets import QLineEdit, QVBoxLayout, QLabel, QHBoxLayout, QGroupBox, QRadioButton, QWidget, QCheckBox

from src.database import DB_ENGINE
from src.gui.widgets.reference_form.form_details_tree import FormDetailsTree

from .ref_page import RefPage
from .util import DummyField


class StartPage(RefPage):
    def __init__(self):
        super().__init__()
        self.setSubTitle('Specify a form name and determine the initial state')

        self.form_name = QLineEdit()
        self.registerField('form.name*', self.form_name)

        self.options_box = QGroupBox()
        self.new_form_button = QRadioButton('Start with an empty form')
        self.existing_form_button = QRadioButton('Copy the settings and fields from an existing form')
        self.existing_forms = FormDetailsTree()

        self.registerField('form.start_new', self.new_form_button)
        self.registerField('form.copy_existing', self.existing_form_button)

        self.dummy = DummyField()
        self.registerField('form.existing_id', self.dummy, property='custom_value')

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

    #
    # Qt overrides
    #
    def validatePage(self) -> bool:
        selected = self.existing_forms.selectedItems()[0]
        self.setField('form.existing_id', str(selected.data(0, Qt.ItemDataRole.UserRole)))
        return True
