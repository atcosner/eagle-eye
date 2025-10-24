from src.database.fields.circled_field import CircledField

from ..util.details_tree import DetailsTree, TextItem, BoxBoundsDetails


class CircledDetails(DetailsTree):
    def __init__(self):
        super().__init__()
        self._options: list[TextItem] = []

        self.name_item = TextItem(self, 'Name')
        self.visual_region_item = BoxBoundsDetails(self, 'Visual Region')
        self.options_item = TextItem(self, 'Options')

        self.resizeColumnToContents(0)

    def load_field(self, field: CircledField) -> None:
        self.name_item.load(field.name)
        self.visual_region_item.load_bounds(field.visual_region)

        for option in field.options:
            option_details = TextItem(self.options_item, option.name)
            self._options.append(option_details)

            visual_region = BoxBoundsDetails(option_details, 'Visual Region')
            visual_region.load_bounds(option.region)
