from PyQt6.QtGui import QIntValidator
from sqlalchemy.orm import Session

from PyQt6.QtWidgets import QRadioButton, QGroupBox, QVBoxLayout, QLabel, QGridLayout, QTextEdit, QLineEdit, QHBoxLayout

from src.database import DB_ENGINE
from src.database.reference_form import ReferenceForm
from src.util.types import FormAlignmentMethod, get_alignment_explanation

from .ref_page import RefPage
from .util import DummyField


class AlignmentPage(RefPage):
    def __init__(self):
        super().__init__()
        self.setSubTitle('How should you reference form be aligned?')

        self.dummy1 = DummyField()
        self.registerField('form.align_method', self.dummy1, property='custom_value')
        self.dummy2 = DummyField()
        self.registerField('form.align_marks', self.dummy2, property='custom_value')

        self.options = QGroupBox()
        self.auto_alignment_button = QRadioButton()
        self.reference_marks_button = QRadioButton()

        self.auto_text_edit = QTextEdit(get_alignment_explanation(FormAlignmentMethod.AUTOMATIC))
        self.marks_text_edit = QTextEdit(get_alignment_explanation(FormAlignmentMethod.ALIGNMENT_MARKS))

        self.reference_marks_edit = QLineEdit()
        self.reference_marks_edit.setValidator(QIntValidator(1, 100))
        self.reference_marks_edit.setText('1')

        self.auto_text_edit.setReadOnly(True)
        self.marks_text_edit.setReadOnly(True)

        self._set_up_layout()

    def _set_up_layout(self) -> None:
        options_layout = QGridLayout()
        options_layout.addWidget(self.auto_alignment_button, 0, 0)
        options_layout.addWidget(QLabel('Automatic Alignment'), 0, 1)
        options_layout.addWidget(self.auto_text_edit, 0, 2)

        count_layout = QHBoxLayout()
        count_layout.addWidget(QLabel('Number of marks:'))
        count_layout.addWidget(self.reference_marks_edit)

        ref_marks_layout = QVBoxLayout()
        ref_marks_layout.addWidget(self.marks_text_edit)
        ref_marks_layout.addLayout(count_layout)

        options_layout.addWidget(self.reference_marks_button, 1, 0)
        options_layout.addWidget(QLabel('Reference Marks'), 1, 1)
        options_layout.addLayout(ref_marks_layout, 1, 2)
        self.options.setLayout(options_layout)

        layout = QVBoxLayout()
        layout.addWidget(QLabel('What method should be used to align forms to the reference form?'))
        layout.addSpacing(10)
        layout.addWidget(self.options)
        self.setLayout(layout)

    def get_alignment_method(self) -> FormAlignmentMethod:
        if self.auto_alignment_button.isChecked():
            return FormAlignmentMethod.AUTOMATIC
        elif self.reference_marks_button.isChecked():
            return FormAlignmentMethod.ALIGNMENT_MARKS
        else:
            raise Exception('No alignment method selected')

    def get_alignment_marks(self) -> int | None:
        if self.reference_marks_button.isChecked():
            return int(self.reference_marks_edit.text())
        else:
            return None

    #
    # Qt overrides
    #
    def initializePage(self) -> None:
        # set the default region count
        if self.field('form.copy_existing'):
            with Session(DB_ENGINE) as session:
                form = session.get(ReferenceForm, self.field('form.existing_id'))
                if form.alignment_method is FormAlignmentMethod.AUTOMATIC:
                    self.auto_alignment_button.setChecked(True)
                else:
                    self.reference_marks_button.setChecked(True)
                    self.reference_marks_edit.setText(str(form.alignment_mark_count))
        else:
            self.auto_alignment_button.setChecked(True)

    def validatePage(self) -> bool:
        self.setField('form.align_method', str(self.get_alignment_method().name))
        self.setField('form.align_marks', self.get_alignment_marks())
        return True
