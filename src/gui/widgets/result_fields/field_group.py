import logging

from PyQt6.QtWidgets import QGridLayout

from src.database.processed_fields.processed_field_group import ProcessedFieldGroup

from .base import BaseField
from .checkbox_field import CheckboxField
from .circled_field import CircledField
from .multi_checkbox_field import MultiCheckboxField
from .text_field import TextField
from .util import wrap_in_frame

logger = logging.getLogger(__name__)


class FieldGroup(BaseField):
    def __init__(self, group: ProcessedFieldGroup):
        super().__init__()

        self.subgrid = QGridLayout()
        self.field_widgets: list[BaseField] = []

        self.load_field(group)

    def load_field(self, group: ProcessedFieldGroup) -> None:
        super().load_field(group)

        # add all fields in this group to our own grid
        for field in group.fields:
            if field.text_field is not None:
                logger.debug(f'Adding text field: {field.text_field.name}')
                field_widget = TextField(field.text_field)

            elif field.checkbox_field is not None:
                logger.debug(f'Adding checkbox field: {field.checkbox_field.name}')
                field_widget = CheckboxField(field.checkbox_field)

            elif field.multi_checkbox_field is not None:
                logger.debug(f'Adding multi checkbox field: {field.multi_checkbox_field.name}')
                field_widget = MultiCheckboxField(field.multi_checkbox_field)

            elif field.circled_field is not None:
                logger.debug(f'Adding circled field: {field.circled_field.name}')
                field_widget = CircledField(field.circled_field)

            else:
                logger.error(f'Processed field ({field.id}) did not have a field we could display')
                continue

            # add the specific field to the group
            row_idx = self.subgrid.rowCount()
            field_widget.add_to_grid(row_idx, self.subgrid)

            # pass through the unverified signal to the region
            field_widget.flagUnverified.connect(self.flagUnverified)
            self.field_widgets.append(field_widget)

    def add_to_grid(self, row_idx: int, grid: QGridLayout) -> None:
        super().add_to_grid(row_idx, grid)
        grid.addWidget(wrap_in_frame(self.subgrid), row_idx, 2)

    #
    # TODO: have our validation status be a composite of all the subfields
    #
