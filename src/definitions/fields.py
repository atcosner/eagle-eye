import copy
from typing import NamedTuple, get_args

from src.definitions.util import BoxBounds


class TextField(NamedTuple):
    name: str
    region: BoxBounds


class MultilineTextField(NamedTuple):
    name: str
    regions: list[BoxBounds]


class TextFieldOrCheckbox(NamedTuple):
    name: str
    visual_region: BoxBounds
    text_region: BoxBounds
    checkbox_region: BoxBounds
    checkbox_text: str


class CheckboxOptionField(NamedTuple):
    name: str
    region: BoxBounds
    text_region: BoxBounds | None = None


class MultiCheckboxField(NamedTuple):
    name: str
    visual_region: BoxBounds
    options: list[CheckboxOptionField]


class CheckboxField(NamedTuple):
    name: str
    region: BoxBounds
    visual_region: BoxBounds


FormField = TextField | MultilineTextField | TextFieldOrCheckbox | MultiCheckboxField | CheckboxField | CheckboxOptionField


def offset_object(item: object, y_offset: int) -> object:
    if isinstance(item, BoxBounds):
        return item._replace(y=item.y + y_offset)
    elif isinstance(item, list):
        return [offset_object(part, y_offset) for part in item]
    else:
        return item


def create_field_with_offset(field: FormField, y_offset: int) -> FormField:
    replacements = {}
    for key, value in field._asdict().items():
        if isinstance(value, get_args(FormField)):
            # Recurse to replace the entire object
            replacements[key] = create_field_with_offset(value, y_offset)
        elif isinstance(value, list) and isinstance(value[0], get_args(FormField)):
            # Recuse for collections of form fields
            replacements[key] = [create_field_with_offset(part, y_offset) for part in value]
        else:
            # Replacements that do not require recursion
            replacements[key] = offset_object(value, y_offset)

    return field._replace(**replacements)
