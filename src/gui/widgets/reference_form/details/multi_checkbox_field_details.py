from src.database.fields.multi_checkbox_field import MultiCheckboxField

from src.gui.widgets.util.details.base_field_details import BaseFieldDetails
from src.gui.widgets.util.details.box_bounds_details import BoxBoundsDetails
from src.gui.widgets.util.details.text_details import TextDetails


class MultiCheckboxFieldDetails(BaseFieldDetails):
    def __init__(self):
        super().__init__()

        # self.validator
        self.options = TextDetails(self, 'Options')
        self._checkboxes: list[TextDetails] = []

        self.resizeColumnToContents(0)

    def load(self, field: MultiCheckboxField) -> None:
        super()._load(field.name, field.visual_region)

        for option in field.checkboxes:
            option_details = TextDetails(self.options, option.name)
            self._checkboxes.append(option_details)

            cb_region = BoxBoundsDetails(option_details, 'Checkbox Region')
            cb_region.load(option.region)

            if option.text_region:
                text_region = BoxBoundsDetails(option_details, 'Text Region')
                text_region.load(option.text_region)
