from sqlalchemy import select
from sqlalchemy.orm import Session

from PyQt6.QtCore import pyqtSlot, Qt
from PyQt6.QtWidgets import (
    QDialog, QWidget, QTreeWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTreeWidgetItem, QHeaderView,
    QMessageBox,
)

from src.database import DB_ENGINE
from src.database.reference_form import ReferenceForm


class ReferenceFormSelector(QDialog):
    def __init__(self, parent: QWidget | None):
        super().__init__(parent)
        self.setWindowTitle('Reference Form Selector')
        self.setMinimumWidth(600)

        self.form_tree = QTreeWidget()
        self.form_tree.setColumnCount(5)
        self.form_tree.setHeaderLabels(['Name', 'Alignment Marks', 'Link Method', 'Regions', 'Fields'])
        self.form_tree.setRootIsDecorated(False)

        # set column 0 (form name) to consume all extra space
        self.form_tree.header().setStretchLastSection(False)
        self.form_tree.header().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)

        self.view_button = QPushButton('View')
        self.view_button.pressed.connect(self.handle_open_form)

        self._set_up_layout()
        self._load_reference_forms()

        # resize all columns to their contents
        for idx in range(self.form_tree.columnCount()):
            self.form_tree.resizeColumnToContents(idx)

    def _set_up_layout(self) -> None:
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(self.view_button)

        layout = QVBoxLayout()
        layout.addWidget(self.form_tree)
        layout.addLayout(button_layout)
        self.setLayout(layout)

    def _load_reference_forms(self) -> None:
        self.form_tree.clear()

        with Session(DB_ENGINE) as session:
            for form in session.scalars(select(ReferenceForm)):
                item = QTreeWidgetItem(
                    None,
                    [
                        form.name,
                        str(form.alignment_mark_count),
                        form.linking_method.name,
                        str(len(form.regions)),
                        str(sum([len(region.fields) for region in form.regions.values()])),
                    ],
                )
                item.setData(0, Qt.ItemDataRole.UserRole, form.id)
                self.form_tree.addTopLevelItem(item)

        # if we loaded any forms, select the first one
        if self.form_tree.topLevelItemCount():
            self.form_tree.setCurrentItem(self.form_tree.topLevelItem(self.form_tree.topLevelItemCount() - 1))

    def get_selected_form(self) -> int:
        selected_item = self.form_tree.selectedItems()[0]
        return selected_item.data(0, Qt.ItemDataRole.UserRole)

    @pyqtSlot()
    def handle_open_form(self) -> None:
        # ensure we have a form selected
        if not self.form_tree.selectedItems():
            QMessageBox.critical(self, 'Error', 'Please select a reference form.')
            return

        self.accept()
