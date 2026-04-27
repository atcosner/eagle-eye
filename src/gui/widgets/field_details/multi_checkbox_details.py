from src.database.fields.multi_checkbox_field import MultiCheckboxField

from ..util.details_tree import BaseFieldDetails, TextItem, BoxBoundsDetails


class MultiCheckboxDetails(BaseFieldDetails):
    def __init__(self):
        super().__init__()

        # self.validator
        self.options = TextItem(self, 'Options')
        self._checkboxes: list[TextItem] = []

        self.resizeColumnToContents(0)

    def load(self, field: MultiCheckboxField) -> None:
        super()._load(field.name, field.visual_region)

        for option in field.checkboxes:
            option_details = TextItem(self.options, option.name)
            self._checkboxes.append(option_details)

            cb_region = BoxBoundsDetails(option_details, 'Checkbox Region')
            cb_region.load(option.region)

            if option.text_region:
                text_region = BoxBoundsDetails(option_details, 'Text Region')
                text_region.load(option.text_region)
