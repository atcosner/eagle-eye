import copy
from collections.abc import Iterable
from dataclasses import dataclass
from typing import NamedTuple, get_args, Callable

from src.definitions.util import BoxBounds


@dataclass
class FormField:
    name: str
    visual_region: BoxBounds


@dataclass
class TextField(FormField):
    validation_function: Callable[[str], bool] = lambda x: True
    allow_copy: bool | None = None


@dataclass
class MultilineTextField(FormField):
    line_regions: list[BoxBounds]


@dataclass
class TextFieldOrCheckbox(FormField):
    text_region: BoxBounds
    checkbox_region: BoxBounds
    checkbox_text: str


@dataclass
# Explicitly not a 'FormField' since it cannot stand alone
class CheckboxOptionField:
    name: str
    region: BoxBounds
    text_region: BoxBounds | None = None


@dataclass
class MultiCheckboxField(FormField):
    options: list[CheckboxOptionField]


@dataclass
class CheckboxField(FormField):
    checkbox_region: BoxBounds


def offset_object(item: object, y_offset: int) -> object | None:
    if isinstance(item, BoxBounds):
        return item._replace(y=item.y + y_offset)
    elif isinstance(item, list):
        return [offset_object(part, y_offset) for part in item if offset_object(part, y_offset) is not None]
    else:
        return None


def create_field_with_offset(field: FormField, y_offset: int) -> FormField:
    replacements = {}
    for key, value in vars(field).items():
        # Throw out callables and dunder functions
        if callable(value) or key.startswith('__'):
            continue

        if isinstance(value, FormField):
            # Recurse to replace the entire object
            replacements[key] = create_field_with_offset(value, y_offset)
        elif isinstance(value, list) and isinstance(value[0], FormField):
            # Recuse for collections of form fields
            replacements[key] = [create_field_with_offset(part, y_offset) for part in value]
        else:
            # Replacements that do not require recursion

            # Edge Case: 'allow_copy'
            if key == 'allow_copy':
                # This can either be a bool or None. If this is set to a bool, replace it with 'True' in the new object
                # i.e. Locality has allow_copy=False in the top section, so we need to override it to True for the bottom
                if value is not None:
                    replacements[key] = True
            else:
                if (new_value := offset_object(value, y_offset)) is not None:
                    replacements[key] = new_value

    # Deep copy the object and then perform replacements
    new_field = copy.deepcopy(field)
    for key, value in replacements.items():
        setattr(new_field, key, value)

    return new_field
