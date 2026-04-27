from PyQt6.QtWidgets import QWidget

from src.database.fields.field_group import FieldGroup

from ...util.details_tree import BaseFieldDetails, TextItem


class FieldGroupDetails(BaseFieldDetails):
    def __init__(self, parent: QWidget, group: FieldGroup):
        super().__init__()
        self.setParent(parent)

        self.name = ''
        self.field_count_item = TextItem(self, 'Field Count')

        self.load(group)

    def load(self, group: FieldGroup) -> None:
        self.name = group.name
        super()._load(self.name, None)
        self.field_count_item.load(len(group.fields))

    def get_name(self) -> str:
        return self.name
