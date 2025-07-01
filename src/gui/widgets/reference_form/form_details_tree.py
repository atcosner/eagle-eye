from sqlalchemy import select
from sqlalchemy.orm import Session

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QTreeWidget, QHeaderView, QTreeWidgetItem
from src.database.reference_form import ReferenceForm


class FormDetailsTree(QTreeWidget):
    def __init__(self, add_checkboxes: bool = False):
        super().__init__()
        self._add_checkboxes = add_checkboxes

        self.setColumnCount(5)
        self.setHeaderLabels(['Name', 'Alignment', 'Link Method', 'Regions', 'Fields'])
        self.setRootIsDecorated(False)

        # set column 0 (form name) to consume all extra space
        self.header().setStretchLastSection(False)
        self.header().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)

    def resize_columns(self) -> None:
        for idx in range(self.columnCount()):
            self.resizeColumnToContents(idx)

    def load_reference_forms(self, session: Session) -> None:
        self.clear()

        for form in session.scalars(select(ReferenceForm)):
            item = QTreeWidgetItem(
                None,
                [
                    form.name,
                    form.alignment_description(),
                    form.linking_method.name,
                    str(len(form.regions)),
                    str(sum([len(region.fields) for region in form.regions.values()])),
                ],
            )
            item.setData(0, Qt.ItemDataRole.UserRole, form.id)
            if self._add_checkboxes:
                item.setCheckState(0, Qt.CheckState.Unchecked)
            self.addTopLevelItem(item)

        # if we loaded any forms, select the first one
        if self.topLevelItemCount():
            self.setCurrentItem(self.topLevelItem(self.topLevelItemCount() - 1))

        self.resize_columns()

    def get_checked_items(self) -> list[QTreeWidgetItem]:
        checked_items = []

        for idx in range(self.topLevelItemCount()):
            item = self.topLevelItem(idx)
            if item.checkState(0) == Qt.CheckState.Checked:
                checked_items.append(item)

        return checked_items
