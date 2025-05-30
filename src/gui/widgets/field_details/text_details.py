from src.database.fields.text_field import TextField

from ..util.details_tree import DetailsTree, TextItem, BoxBoundsDetails


class TextDetails(DetailsTree):
    def __init__(self):
        super().__init__()

        self.name = TextItem(self, 'Name')
        self.visual_region = BoxBoundsDetails(self, 'Visual Region')
        self.allow_copy = TextItem(self, 'Allow Copy')

        self.resizeColumnToContents(0)

    def load_field(self, field: TextField) -> None:
        self.name.load(field.name)
        self.visual_region.load_bounds(field.visual_region)
        self.allow_copy.load(field.allow_copy)
