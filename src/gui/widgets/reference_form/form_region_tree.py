import logging
from sqlalchemy.orm import Session

from PyQt6.QtCore import QSize, pyqtSignal, pyqtSlot
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QTreeWidget, QTreeWidgetItem, QHeaderView

from src.database import DB_ENGINE
from src.database.fields.field_group import FieldGroup
from src.database.fields.form_field import FormField
from src.database.form_region import FormRegion
from src.database.reference_form import ReferenceForm
from src.util.fields import get_field_name_and_type
from src.util.resources import GENERIC_ICON_PATH

from .util import SelectionType
from ..util.colors import get_icon_for_region

logger = logging.getLogger(__name__)


class TreeItem(QTreeWidgetItem):
    def __init__(self, db_id: int):
        super().__init__()
        self._db_id: int = db_id

    def get_db_id(self) -> int:
        assert self._db_id is not None
        return self._db_id


class FieldItem(TreeItem):
    def __init__(self, field: FormField):
        super().__init__(field.id)

        field_name, field_type = get_field_name_and_type(field)
        self.setText(0, field_name)
        self.setText(1, field_type)
        if field.identifier:
            self.setIcon(0, QIcon(str(GENERIC_ICON_PATH / 'good.png')))


class FieldGroupItem(TreeItem):
    def __init__(self, group: FieldGroup):
        super().__init__(group.id)
        self.setText(0, group.name)

        self._populate(group)

    def _populate(self, group: FieldGroup) -> None:
        for field in group.fields:
            self.addChild(FieldItem(field))

    def get_field(self, db_id: int) -> FieldItem | None:
        for idx in range(self.childCount()):
            child = self.child(idx)
            if child.get_db_id() == db_id:
                return child

        return None


class RegionItem(TreeItem):
    def __init__(self, region: FormRegion):
        super().__init__(region.id)
        self.setText(0, f'Region: {region.name}')

        self._populate(region)

    def _populate(self, region: FormRegion) -> None:
        self.setIcon(0, get_icon_for_region(region.local_id))

        for group in region.groups:
            if len(group.fields) > 1:
                self.addChild(FieldGroupItem(group))
            else:
                self.addChild(FieldItem(group.fields[0]))

    def get_field(self, db_id: int) -> FieldItem | None:
        for idx in range(self.childCount()):
            child = self.child(idx)

            # handle this differently for a field group child vs field item child
            if isinstance(child, FieldGroupItem):
                if (found_field := child.get_field(db_id)) is not None:
                    return found_field
            else:
                if child.get_db_id() == db_id:
                    return child

        return None


def get_selection_type(item: RegionItem | FieldGroupItem | FieldItem) -> SelectionType:
    if isinstance(item, RegionItem):
        return SelectionType.REGION
    elif isinstance(item, FieldGroupItem):
        return SelectionType.FIELD_GROUP
    else:
        return SelectionType.FIELD


class FormRegionTree(QTreeWidget):
    updateDetails = pyqtSignal(SelectionType, int)

    def __init__(self):
        super().__init__()
        self._form_db_id: int | None = None

        self.setColumnCount(2)
        self.setHeaderLabels(['Name', 'Field Type'])
        self.setIconSize(QSize(10, 10))

        self.header().setStretchLastSection(False)
        self.header().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)

        self.currentItemChanged.connect(self.handle_current_item_change)

    def load_reference_form(self, form: ReferenceForm | int | None) -> None:
        self._form_db_id = None
        if form is None:
            return

        with Session(DB_ENGINE) as session:
            form = session.get(ReferenceForm, form) if isinstance(form, int) else form
            self._form_db_id = form.id

            for region in form.regions.values():
                self.addTopLevelItem(RegionItem(region))

    def update_selection(self, selection: SelectionType, db_id: int) -> None:
        if selection is SelectionType.FIELD:
            for idx in range(self.topLevelItemCount()):
                region = self.topLevelItem(idx)
                if (matched_field := region.get_field(db_id)) is not None:
                    self.setCurrentItem(matched_field)
                    return

            logger.warning(f'Did not find a field with ID: {db_id}')

        elif selection is SelectionType.REGION:
            # TODO: implement this
            pass

        else:
            logger.error(f'Unknown selection type: {selection}')

    @pyqtSlot(QTreeWidgetItem, QTreeWidgetItem)
    def handle_current_item_change(self, current: TreeItem, _: TreeItem) -> None:
        self.updateDetails.emit(get_selection_type(current), current.get_db_id())

    def delete_selected_item(self) -> tuple[SelectionType, int] | None:
        selected_items = self.selectedItems()
        if not selected_items:
            return None

        current = selected_items[0]
        selection_type = get_selection_type(current)
        db_id = current.get_db_id()

        # remove the item from the tree
        if parent := current.parent():
            parent.takeChild(parent.indexOfChild(current))
        else:
            self.takeTopLevelItem(self.indexOfTopLevelItem(current))

        return selection_type, db_id
