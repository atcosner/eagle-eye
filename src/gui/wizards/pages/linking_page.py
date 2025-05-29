from sqlalchemy.orm import Session

from PyQt6.QtCore import pyqtSlot
from PyQt6.QtWidgets import QVBoxLayout, QLabel, QRadioButton, QGroupBox, QTextEdit, QCheckBox

from src.database import DB_ENGINE
from src.database.reference_form import ReferenceForm
from src.util.types import FormLinkingMethod, get_link_explanation

from .base import BasePage
from .util import DummyField


class LinkingPage(BasePage):
    def __init__(self):
        super().__init__()
        self.setSubTitle('Will your form allow linking fields?')

        self.group = QGroupBox()
        self.option_explanation = QTextEdit()
        self.option_explanation.setReadOnly(True)
        self.option_explanation.setAcceptRichText(True)

        self.dummy = DummyField()
        self.registerField('form.link_method', self.dummy, property='custom_value')

        self.options: list[QRadioButton] = []
        for value in FormLinkingMethod:
            nice_name = value.name.lower().replace('_', ' ').title()
            button = QRadioButton(nice_name)
            button.toggled.connect(self.handle_method_toggle)
            self.options.append(button)

        self._set_up_layout()
        self.options[0].setChecked(True)

    def _set_up_layout(self) -> None:
        group_layout = QVBoxLayout()
        for option in self.options:
            group_layout.addWidget(option)
        self.group.setLayout(group_layout)

        layout = QVBoxLayout()
        layout.addWidget(QLabel('Will fields be allowed to be linked across regions/forms?'))
        layout.addSpacing(10)
        layout.addWidget(self.group)
        layout.addWidget(self.option_explanation)
        layout.addStretch()
        self.setLayout(layout)

    def get_link_method(self) -> FormLinkingMethod:
        for option in self.options:
            if option.isChecked():
                name = option.text()
                return FormLinkingMethod[name.replace(' ', '_').upper()]

        raise RuntimeError('No link method selected')

    @pyqtSlot()
    def handle_method_toggle(self) -> None:
        method = self.get_link_method()
        self.option_explanation.setText(get_link_explanation(method))
        self.setField('form.link_method', str(method.name))

    #
    # Qt overrides
    #
    def initializePage(self) -> None:
        if self.field('form.copy_existing'):
            with Session(DB_ENGINE) as session:
                form = session.get(ReferenceForm, self.field('form.existing_id'))
                for option in self.options:
                    value = FormLinkingMethod[option.text().replace(' ', '_').upper()]
                    if value == form.linking_method:
                        option.setChecked(True)

    def validatePage(self) -> bool:
        self.setField('form.link_method', str(self.get_link_method().name))
        return True
