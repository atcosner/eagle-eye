from src.database.fields.text_field import TextField

from ..util.details_tree import BaseFieldDetails, TextItem


class TextDetails(BaseFieldDetails):
    def __init__(self):
        super().__init__()

        self.allow_copy = TextItem(self, 'Allow Copy')

        self.resizeColumnToContents(0)

    def load(self, field: TextField) -> None:
        super()._load(field.name, field.visual_region)
        self.allow_copy.load(field.allow_copy)
