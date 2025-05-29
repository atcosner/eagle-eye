from src.database.fields.checkbox_field import CheckboxField

from ..util.details_tree import DetailsTree, TextItem, BoxBoundsDetails


class CheckboxDetails(DetailsTree):
    def __init__(self):
        super().__init__()

        self.name = TextItem(self, 'Name')
        self.visual_region = BoxBoundsDetails(self, 'Visual Region')
        self.checkbox_region = BoxBoundsDetails(self, 'Checkbox Region')

        self.resizeColumnToContents(0)

    def load_field(self, field: CheckboxField) -> None:
        self.name.load(field.name)
        self.visual_region.load_bounds(field.visual_region)
        self.checkbox_region.load_bounds(field.checkbox_region)
