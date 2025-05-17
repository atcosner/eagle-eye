import logging

from ..database.fields.form_field import FormField

logger = logging.getLogger(__name__)


def get_field_name_and_type(field: FormField) -> tuple[str | None, str | None]:
    if field.text_field is not None:
        return field.text_field.name, 'Text'
    elif field.checkbox_field is not None:
        return field.checkbox_field.name, 'Checkbox'
    elif field.multi_checkbox_field is not None:
        return field.multi_checkbox_field.name, 'Multi Checkbox'
    else:
        logger.error(f'Field {field.id} did not have any sub-fields! ')
        return None, None
