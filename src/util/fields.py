import logging

from ..database.fields.form_field import FormField

logger = logging.getLogger(__name__)


def get_field_name(field: FormField) -> str | None:
    if field.text_field is not None:
        return field.text_field.name
    elif field.multiline_text_field is not None:
        return field.multiline_text_field.name
    elif field.checkbox_field is not None:
        return field.checkbox_field.name
    elif field.multi_checkbox_field is not None:
        return field.multi_checkbox_field.name
    else:
        logger.error(f'Field {field.id} did not have any sub-fields! ')
        return None
