from src.database.fields.circled_field import CircledField
from src.util.validation import MultiChoiceValidation

from src.gui.widgets.util.details.base_field_details import BaseFieldDetails
from src.gui.widgets.util.details.box_bounds_details import BoxBoundsDetails
from src.gui.widgets.util.details.enum_details import EnumDetails
from src.gui.widgets.util.details.text_details import TextDetails


class CircledFieldDetails(BaseFieldDetails):
    def __init__(self):
        super().__init__()
        self._options: list[TextDetails] = []

        self.validator_item = EnumDetails(self, 'Validator', MultiChoiceValidation)
        self.options_item = TextDetails(self, 'Options')

        self.resizeColumnToContents(0)

    def load(self, field: CircledField) -> None:
        super()._load(field.name, field.visual_region)

        self.validator_item.load_data(field.validator)

        for option in field.options:
            option_details = TextDetails(self.options_item, option.name)
            self._options.append(option_details)

            visual_region = BoxBoundsDetails(option_details, 'Visual Region')
            visual_region.load(option.region)
