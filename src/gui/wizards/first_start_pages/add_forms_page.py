import logging
from sqlalchemy.orm import Session
from typing import Callable

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QVBoxLayout, QLabel, QTreeWidget, QTreeWidgetItem, QHeaderView, QApplication

from src.database import DB_ENGINE
from src.examples import EXAMPLE_FORMS
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
        for form in EXAMPLE_FORMS:
            item = QTreeWidgetItem(None)
            item.setText(0, form.name)
            item.setCheckState(0, Qt.CheckState.Unchecked)
            item.setData(0, Qt.ItemDataRole.UserRole, form.build_func)

            item.setText(1, str(form.alignment_method))
            item.setText(2, str(form.link_method))
            item.setText(3, str(form.regions))
            self.form_tree.addTopLevelItem(item)

    #
    # Qt overrides
    #

    def validatePage(self) -> bool:
        # add any selected reference forms
        logger.info('Adding reference forms to the DB')
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)

        with Session(DB_ENGINE) as session:
            for index in range(self.form_tree.topLevelItemCount()):
                item = self.form_tree.topLevelItem(index)
                if item.checkState(0) == Qt.CheckState.Checked:
                    # call the build function to add this form into the DB
                    logger.info(f'Adding: {item.text(0)}')
                    with Session(DB_ENGINE) as session:
                        build_func: Callable = item.data(0, Qt.ItemDataRole.UserRole)
                        build_func(session)

        # save the Google API settings
        logger.info('Updating Google API settings')
        save_api_settings()

        QApplication.restoreOverrideCursor()
        return True
