from src.database.fields.text_field import TextField

from src.gui.widgets.util.details.base_field_details import BaseFieldDetails
from src.gui.widgets.util.details.text_details import TextDetails


class TextFieldDetails(BaseFieldDetails):
    def __init__(self):
        super().__init__()

        self.allow_copy = TextDetails(self, 'Allow Copy')

        self.resizeColumnToContents(0)

    def load(self, field: TextField) -> None:
        super()._load(field.name, field.visual_region)
        self.allow_copy.load(field.allow_copy)
