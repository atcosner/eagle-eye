from sqlalchemy.orm import Session

from PyQt6.QtCore import QSize, pyqtSignal, pyqtSlot
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QTreeWidget, QTreeWidgetItem, QHeaderView

from src.database import DB_ENGINE
from src.database.fields.form_field import FormField
from src.database.form_region import FormRegion
from src.database.reference_form import ReferenceForm
from src.util.fields import get_field_name_and_type
from src.util.resources import GENERIC_ICON_PATH

from .util import SelectionType
from ..util.colors import get_icon_for_region


class TreeItem(QTreeWidgetItem):
    def __init__(self, db_id: int):
        super().__init__()
        self._field_db_id: int = db_id

    def get_db_id(self) -> int:
        assert self._field_db_id is not None
        return self._field_db_id


class FieldItem(TreeItem):
    def __init__(self, field: FormField):
        super().__init__(field.id)

        field_name, field_type = get_field_name_and_type(field)
        self.setText(0, field_name)
        self.setText(1, field_type)
        if field.identifier:
            self.setIcon(0, QIcon(str(GENERIC_ICON_PATH / 'good.png')))


class RegionItem(TreeItem):
    def __init__(self, region: FormRegion):
        super().__init__(region.id)

        self.setText(0, f'Region: {region.name}')

        self._populate(region)

    def _populate(self, region: FormRegion) -> None:
        self.setIcon(0, get_icon_for_region(region.local_id))
        for field in region.fields:
            self.addChild(FieldItem(field))


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

    @pyqtSlot(QTreeWidgetItem, QTreeWidgetItem)
    def handle_current_item_change(self, current: TreeItem, _: TreeItem) -> None:
        selection = SelectionType.REGION if isinstance(current, RegionItem) else SelectionType.FIELD
        self.updateDetails.emit(selection, current.get_db_id())
