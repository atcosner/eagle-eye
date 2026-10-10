import logging
from sqlalchemy.orm import Session

from PyQt6.QtCore import pyqtSlot, Qt
from PyQt6.QtWidgets import (
    QDialog, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QMessageBox, QLabel, QTreeWidget, QTreeWidgetItem,
    QHeaderView, QApplication,
)

from src.database import DB_ENGINE
from src.examples import EXAMPLE_FORMS

logger = logging.getLogger(__name__)


class ExampleFormAdder(QDialog):
    def __init__(self, parent: QWidget | None):
        super().__init__(parent)
        self.setWindowTitle('Add Example Reference Forms')
        self.setMinimumWidth(600)

        self.form_tree = QTreeWidget()
        self.form_tree.setColumnCount(4)
        self.form_tree.setHeaderLabels(['Name', 'Alignment', 'Link Method', 'Regions'])
        self.form_tree.setRootIsDecorated(False)
        self.form_tree.header().setStretchLastSection(False)
        self.form_tree.header().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)

        self.add_button = QPushButton('Add')
        self.add_button.pressed.connect(self.handle_add_forms)

        self.close_button = QPushButton('Close')
        self.close_button.pressed.connect(self.reject)

        self._set_up_layout()
        self._add_forms()

    def _set_up_layout(self) -> None:
        info_text = QLabel(
            'Eagle Eye comes with several reference forms used by the KU Biodiversity Institute for their collections.\n'
            'These can be added to your install as examples for how to create your own reference forms.\n'
            'Select any of the below reference forms to install them.'
        )
        margins = info_text.contentsMargins()
        margins.setBottom(10)
        info_text.setContentsMargins(margins)

        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.close_button)

        layout = QVBoxLayout()
        layout.addWidget(info_text)
        layout.addWidget(self.form_tree)
        layout.addLayout(button_layout)
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

    @pyqtSlot()
    def handle_add_forms(self) -> None:
        add_functions = []
        for index in range(self.form_tree.topLevelItemCount()):
            item = self.form_tree.topLevelItem(index)
            if item.checkState(0) == Qt.CheckState.Checked:
                add_functions.append(item.data(0, Qt.ItemDataRole.UserRole))

        if not add_functions:
            QMessageBox.warning(self, 'Selection Error', 'Please select at least one form.')
            return

        # adding forms can take some time, so show a busy cursor
        logger.info('Adding example reference forms to the DB')
        self.setDisabled(True)
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        try:
            with Session(DB_ENGINE) as session:
                for add_function in add_functions:
                    add_function(session)
        except Exception as e:
            logger.exception('Failed to add example reference forms')
            QApplication.restoreOverrideCursor()
            self.setDisabled(False)
            QMessageBox.critical(self, 'Add Error', f'Failed to add the example reference forms:\n{e}')
            return

        QApplication.restoreOverrideCursor()
        self.setDisabled(False)

        QMessageBox.information(
            self,
            'Add Success',
            f'Successfully added {len(add_functions)} reference form(s)',
        )
        self.accept()
