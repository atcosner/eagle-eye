from PyQt6.QtCore import QRect
from PyQt6.QtWidgets import QTreeWidget

from .box_bounds_details import BoxBoundsDetails
from .text_details import TextDetails

from src.util.types import BoxBounds


class BaseFieldDetails(QTreeWidget):
    def __init__(self):
        super().__init__()

        self.name_item = TextDetails(self, 'Name')
        self.visual_region_item  = BoxBoundsDetails(self, 'Visual Region')

        self.setColumnCount(2)
        self.setHeaderLabels(['Setting', 'Value'])
    
    def _load(self, name: str, bounds: BoxBounds | None) -> None:
        self.name_item.load(name)
        if bounds is not None:
            self.visual_region_item.load(bounds)
        else:
            self.visual_region_item.setHidden(True)
    
    def update_position(self, position: QRect) -> None:
        self.visual_region_item.update_position(position)
