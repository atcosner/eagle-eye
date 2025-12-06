from PyQt6.QtWidgets import QWidget

from src.database.fields.field_group import FieldGroup

from ...util.details_tree import DetailsTree, TextItem


class FieldGroupDetails(DetailsTree):
    def __init__(self, parent: QWidget, group: FieldGroup):
        super().__init__()
        self.setParent(parent)

        self.name = None
        self.name_item = TextItem(self, 'Name')
        self.field_count_item = TextItem(self, 'Field Count')

        self._load(group)

    def _load(self, group: FieldGroup) -> None:
        self.name = group.name
        self.name_item.load(group.name)
        self.field_count_item.load(len(group.fields))

    def get_name(self) -> str:
        return self.name
