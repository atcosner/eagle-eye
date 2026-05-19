import logging
from collections import defaultdict
from sqlalchemy.orm import Session

from PyQt6.QtCore import pyqtSignal, pyqtSlot, QRect
from PyQt6.QtGui import QPixmap, QColor
from PyQt6.QtWidgets import QGraphicsScene, QGraphicsPixmapItem, QGraphicsItemGroup

from src.database import DB_ENGINE
from src.database.reference_form import ReferenceForm

from .fields.base import DbSceneField, LabeledField
from .util import SelectionType, RegionGroup
from ..util.colors import REGION_COLORS

logger = logging.getLogger(__name__)

# TODO: implement undo
# https://doc.qt.io/qt-6.8/qtwidgets-tools-undoframework-example.html


class FormScene(QGraphicsScene):
    fieldSelected = pyqtSignal(int)
    fieldPositionUpdate = pyqtSignal(int, QRect)

    def __init__(self):
        super().__init__()
        self._form_db_id: int | None = None

        self.reference_pixmap: QGraphicsPixmapItem | None = None

        self.region_colors: dict[int, QColor] = {}
        self.fields_by_region: dict[int, list[DbSceneField]] = defaultdict(list)
        self.fields_by_id: dict[int, DbSceneField] = {}

        self.region_group: QGraphicsItemGroup | None = None

        self.selectionChanged.connect(self.handle_selection_change)

    def load_reference_form(self, form: ReferenceForm | int | None) -> None:
        self._form_db_id = None
        if form is None:
            return

        with Session(DB_ENGINE) as session:
            form = session.get(ReferenceForm, form) if isinstance(form, int) else form
            self._form_db_id = form.id

            self.reference_pixmap = self.addPixmap(QPixmap(str(form.path)))

            for region in form.regions.values():
                region_color = REGION_COLORS[region.local_id]
                self.region_colors[region.id] = region_color

                # TODO: add a hierarchy level for the field groups
                for group in region.groups:
                    for field in group.fields:
                        qt_field = DbSceneField(field, region_color)
                        qt_field.positionUpdate.connect(self.fieldPositionUpdate)
                        self.addItem(qt_field)

                        self.fields_by_region[region.id].append(qt_field)
                        self.fields_by_id[field.id] = qt_field

    def handle_deletion(self, selection: SelectionType, db_id: int) -> None:
        if selection is SelectionType.REGION:
            fields = self.fields_by_region.pop(db_id)
            for field in fields:
                self.removeItem(field)

            self.destroyItemGroup(self.region_group)
            self.region_group = None
        elif selection is SelectionType.FIELD:
            field = self.fields_by_id.pop(db_id)
            self.removeItem(field)
        else:
            raise RuntimeError(f'Unknown selection type: {selection}')

    def handle_tree_selection_change(self, selection: SelectionType, db_id: int) -> None:
        self.clearSelection()
        if self.region_group is not None:
            self.destroyItemGroup(self.region_group)
            self.region_group = None

        if selection is SelectionType.FIELD:
            field = self.fields_by_id.get(db_id, None)
            if field is not None:
                field.setSelected(True)
            else:
                logger.error(f'Could not find field with ID: {db_id}')

        elif selection is SelectionType.REGION:
            region_items = self.fields_by_region.get(db_id, None)
            if region_items is None:
                logger.error(f'Could not find region with ID: {db_id}')
                return

            self.region_group = RegionGroup(self.region_colors[db_id], region_items)
            self.addItem(self.region_group)
            self.region_group.setSelected(True)
        
        elif selection is SelectionType.FIELD_GROUP:
            pass

        else:
            logger.error(f'Unknown selection type: {selection}')

    @pyqtSlot()
    def handle_selection_change(self) -> None:
        if len(self.selectedItems()) != 1:
            return

        selected = self.selectedItems()[0]
        if isinstance(selected, DbSceneField):
            self.fieldSelected.emit(selected.get_db_id())
        elif isinstance(selected, LabeledField):
            # check if this is a child of a DB field
            parent_item = selected.parentItem()
            if isinstance(parent_item, DbSceneField):
                self.fieldSelected.emit(parent_item.get_db_id())
