import logging
from sqlalchemy.orm import Session

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QVBoxLayout, QLabel, QTreeWidget, QTreeWidgetItem, QHeaderView

from src.database import DB_ENGINE
from src.examples.fn_form_v1 import add_fn_form_v1
from src.examples.kt_form_v8 import add_kt_form_v8
from src.util.google_api import save_api_settings

from ..util.base_page import BasePage

logger = logging.getLogger(__name__)


class AddFormsPage(BasePage):
    def __init__(self):
        super().__init__('Eagle Eye | Add Example Reference Forms')

        self.form_tree = QTreeWidget()
        self.form_tree.setColumnCount(4)
        self.form_tree.setHeaderLabels(['Name', 'Alignment', 'Link Method', 'Regions'])
        self.form_tree.setRootIsDecorated(False)
        self.form_tree.header().setStretchLastSection(False)
        self.form_tree.header().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)

        self._set_up_layout()
        self._add_forms()

    def _set_up_layout(self) -> None:
        welcome_text = QLabel(
            'Eagle Eye comes with several reference forms used by the KU Biodiversity Institute for their collections.\n'
            'These can be added to your install as examples for how to create your own reference forms.\n'
            'Select any of the below reference forms to install them.'
        )
        margins = welcome_text.contentsMargins()
        margins.setBottom(10)
        welcome_text.setContentsMargins(margins)

        layout = QVBoxLayout()
        layout.addWidget(welcome_text)
        layout.addWidget(self.form_tree)
        self.setLayout(layout)

    def _add_forms(self) -> None:
        example_forms = [
            QTreeWidgetItem(None, ['KU Ornithology - KT Form v8', 'Alignment Marks', 'Previous Region', '2']),
            QTreeWidgetItem(None, ['KU Mammalogy - FN Form v1', 'Automatic', 'Previous Identifier', '6']),
        ]

        for form in example_forms:
            form.setCheckState(0, Qt.CheckState.Unchecked)
            self.form_tree.addTopLevelItem(form)

    #
    # Qt overrides
    #

    def validatePage(self) -> bool:
        # TODO: show a dialog since the below operations can take some time to complete

        # add any selected reference forms
        logger.info('Adding reference forms to the DB')
        with Session(DB_ENGINE) as session:
            for index in range(self.form_tree.topLevelItemCount()):
                item = self.form_tree.topLevelItem(index)
                if item.checkState(0) == Qt.CheckState.Checked:
                    # add the form to the DB
                    if index == 0:
                        logger.info('Adding KT Form v8')
                        add_kt_form_v8(session)
                    elif index == 1:
                        logger.info('Adding FN Form v1')
                        add_fn_form_v1(session)

        # save the Google API settings
        logger.info('Updating Google API settings')
        save_api_settings()

        return True
