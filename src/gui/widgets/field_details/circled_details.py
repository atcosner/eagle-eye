from src.database.fields.circled_field import CircledField

from ..util.details_tree import BaseFieldDetails, TextItem, BoxBoundsDetails


class CircledDetails(BaseFieldDetails):
    def __init__(self):
        super().__init__()
        self._options: list[TextItem] = []

        self.options_item = TextItem(self, 'Options')

        self.resizeColumnToContents(0)

    def load(self, field: CircledField) -> None:
        super()._load(field.name, field.visual_region)

        for option in field.options:
            option_details = TextItem(self.options_item, option.name)
            self._options.append(option_details)

            visual_region = BoxBoundsDetails(option_details, 'Visual Region')
            visual_region.load(option.region)
