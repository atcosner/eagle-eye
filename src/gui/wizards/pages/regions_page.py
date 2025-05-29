from sqlalchemy.orm import Session

from PyQt6.QtCore import QSize
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QRadioButton, QGroupBox, QVBoxLayout, QLabel, QGridLayout

from src.database import DB_ENGINE
from src.database.reference_form import ReferenceForm
from src.util.images import scale_pixmap
from src.util.resources import REFERENCE_FORM_ICON_PATH

from .base import BasePage


class RegionsPage(BasePage):
    def __init__(self):
        super().__init__()
        self.setSubTitle('How many regions will your form have?')

        self.options = QGroupBox()
        self.one_region_button = QRadioButton()
        self.two_region_button = QRadioButton()

        self.one_region_label = QLabel()
        self.one_region_label.setPixmap(
            scale_pixmap(
                QPixmap(str(REFERENCE_FORM_ICON_PATH / 'one_region.png')),
                QSize(64, 64),
            )
        )
        self.two_region_label = QLabel()
        self.two_region_label.setPixmap(
            scale_pixmap(
                QPixmap(str(REFERENCE_FORM_ICON_PATH / 'two_regions.png')),
                QSize(64, 64),
            )
        )

        self._set_up_layout()

    def _set_up_layout(self) -> None:
        options_layout = QGridLayout()
        options_layout.addWidget(self.one_region_button, 0, 0)
        options_layout.addWidget(self.one_region_label, 0, 1)
        options_layout.addWidget(QLabel('One Region (one page = one specimen)'), 0, 2)
        options_layout.addWidget(self.two_region_button, 1, 0)
        options_layout.addWidget(self.two_region_label, 1, 1)
        options_layout.addWidget(QLabel('Two Regions (one page = two specimen)'), 1, 2)
        self.options.setLayout(options_layout)

        layout = QVBoxLayout()
        layout.addWidget(QLabel('How many regions will each form have?'))
        layout.addSpacing(10)
        layout.addWidget(self.options)
        self.setLayout(layout)

    #
    # Qt overrides
    #
    def initializePage(self) -> None:
        # set the default region count
        if self.field('form.copy_existing'):
            with Session(DB_ENGINE) as session:
                form = session.get(ReferenceForm, self.field('form.existing_id'))
                if len(form.regions) == 1:
                    self.one_region_button.setChecked(True)
                elif len(form.regions) == 2:
                    self.two_region_button.setChecked(True)
                else:
                    # TODO: more regions?
                    pass
        else:
            self.one_region_button.setChecked(True)
