from src.database.fields.checkbox_field import CheckboxField

from src.gui.widgets.util.details.base_field_details import BaseFieldDetails
from src.gui.widgets.util.details.box_bounds_details import BoxBoundsDetails


class CheckboxFieldDetails(BaseFieldDetails):
    def __init__(self):
        super().__init__()

        self.checkbox_region = BoxBoundsDetails(self, 'Checkbox Region')

        self.resizeColumnToContents(0)

    def load(self, field: CheckboxField) -> None:
        super()._load(field.name, field.visual_region)
        self.checkbox_region.load(field.checkbox_region)
