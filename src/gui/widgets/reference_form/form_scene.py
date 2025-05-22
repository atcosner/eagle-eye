import logging
from collections import defaultdict

from PyQt6.QtCore import pyqtSignal, pyqtSlot
from sqlalchemy.orm import Session

from PyQt6.QtGui import QPixmap, QColor
from PyQt6.QtWidgets import QGraphicsScene, QGraphicsPixmapItem, QGraphicsItemGroup

from src.database import DB_ENGINE
from src.database.reference_form import ReferenceForm

from .fields.base import BaseField
from .util import SelectionType, RegionGroup
from ..util.colors import REGION_COLORS

logger = logging.getLogger(__name__)

# TODO: implement undo
# https://doc.qt.io/qt-6.8/qtwidgets-tools-undoframework-example.html


class FormScene(QGraphicsScene):
    fieldSelected = pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self._form_db_id: int | None = None

        self.reference_pixmap: QGraphicsPixmapItem | None = None

        self.region_colors: dict[int, QColor] = {}
        self.fields_by_region: dict[int, list[BaseField]] = defaultdict(list)
        self.fields_by_id: dict[int, BaseField] = {}

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

                for field in region.fields:
                    qt_field = BaseField(field, region_color)
                    self.addItem(qt_field)

                    self.fields_by_region[region.id].append(qt_field)
                    self.fields_by_id[field.id] = qt_field

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

        else:
            logger.error(f'Unknown selection type: {selection}')

    @pyqtSlot()
    def handle_selection_change(self) -> None:
        if len(self.selectedItems()) != 1:
            return

        selected = self.selectedItems()[0]
        if isinstance(selected, BaseField):
            self.fieldSelected.emit(selected.get_db_id())
