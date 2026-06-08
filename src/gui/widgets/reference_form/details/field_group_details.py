from PyQt6.QtWidgets import QWidget

from src.database.fields.field_group import FieldGroup

from src.gui.widgets.util.details.base_field_details import BaseFieldDetails
from src.gui.widgets.util.details.text_details import TextDetails


class FieldGroupDetails(BaseFieldDetails):
    def __init__(self, parent: QWidget, group: FieldGroup):
        super().__init__()
        self.setParent(parent)

        self.name = ''
        self.field_count_item = TextDetails(self, 'Field Count')

        self.load(group)

    def load(self, group: FieldGroup) -> None:
        self.name = group.name
        super()._load(self.name, None)
        self.field_count_item.load(len(group.fields))

    def get_name(self) -> str:
        return self.name
