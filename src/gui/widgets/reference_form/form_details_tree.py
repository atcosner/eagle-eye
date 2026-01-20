from sqlalchemy import select
from sqlalchemy.orm import Session

from PyQt6.QtCore import Qt, pyqtSignal, pyqtSlot
from PyQt6.QtWidgets import QTreeWidget, QHeaderView, QTreeWidgetItem
from src.database.reference_form import ReferenceForm


class FormDetailsTree(QTreeWidget):
    referenceFormChanged = pyqtSignal(int)

    def __init__(self, add_checkboxes: bool = False):
        super().__init__()
        self._add_checkboxes = add_checkboxes
        self._selected_reference_form_id: int | None = None

        self.setColumnCount(5)
        self.setHeaderLabels(['Name', 'Alignment', 'Link Method', 'Regions', 'Fields'])
        self.setRootIsDecorated(False)

        # set column 0 (form name) to consume all extra space
        self.header().setStretchLastSection(False)
        self.header().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)

        self.currentItemChanged.connect(self.handle_current_item_changed)

    def get_reference_form(self) -> int | None:
        return self._selected_reference_form_id

    def resize_columns(self) -> None:
        for idx in range(self.columnCount()):
            self.resizeColumnToContents(idx)

    def load_reference_forms(self, session: Session) -> None:
        self.clear()

        for form in session.scalars(select(ReferenceForm)):
            # sum up the number of fields
            field_count = 0
            for region in form.regions.values():
                for group in region.groups:
                    field_count += len(group.fields)

            item = QTreeWidgetItem(
                None,
                [
                    form.name,
                    form.alignment_description(),
                    form.linking_method.name,
                    str(len(form.regions)),
                    str(field_count),
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

    def set_reference_form(self, db_id: int | None) -> None:
        for child_id in range(self.topLevelItemCount()):
            item = self.topLevelItem(child_id)

            if item.data(0, Qt.ItemDataRole.UserRole) == db_id:
                self.setCurrentItem(item)
                self.scrollToItem(item)

    @pyqtSlot(QTreeWidgetItem, QTreeWidgetItem)
    def handle_current_item_changed(
            self,
            current: QTreeWidgetItem | None,
            _: QTreeWidgetItem | None,
    ) -> None:
        current_id = current.data(0, Qt.ItemDataRole.UserRole)
        if current_id != self._selected_reference_form_id:
            self.referenceFormChanged.emit(current_id)
            self._selected_reference_form_id = current_id
