from src.database.fields.multi_checkbox_field import MultiCheckboxField

from ..util.details_tree import DetailsTree, TextItem, BoxBoundsDetails


class MultiCheckboxDetails(DetailsTree):
    def __init__(self):
        super().__init__()

        self.name = TextItem(self, 'Name')
        self.visual_region = BoxBoundsDetails(self, 'Visual Region')
        # self.validator
        self.options = TextItem(self, 'Options')
        self._checkboxes: list[TextItem] = []

        self.resizeColumnToContents(0)

    def load_field(self, field: MultiCheckboxField) -> None:
        self.name.load(field.name)
        self.visual_region.load_bounds(field.visual_region)

        for option in field.checkboxes:
            option_details = TextItem(self.options, option.name)
            self._checkboxes.append(option_details)

            cb_region = BoxBoundsDetails(option_details, 'Checkbox Region')
            cb_region.load_bounds(option.region)

            if option.text_region:
                text_region = BoxBoundsDetails(option_details, 'Text Region')
                text_region.load_bounds(option.text_region)
