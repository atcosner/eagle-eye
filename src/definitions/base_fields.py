import copy
from dataclasses import dataclass

from src.validation.multi_checkbox import MultiCheckboxValidator
from src.validation.single_checkbox import SingleCheckboxValidator
from src.validation.text import TextValidator

from .util import BoxBounds


@dataclass
class BaseField:
    name: str
    visual_region: BoxBounds


@dataclass
class TextField(BaseField):
    validator: type[TextValidator]
    allow_copy: bool = False
    # Fields for if this text field has a checkbox with default language
    text_region: BoxBounds | None = None
    checkbox_region: BoxBounds | None = None
    checkbox_text: str | None = None


@dataclass
class MultilineTextField(BaseField):
    validator: type[TextValidator]
    line_regions: list[BoxBounds]


@dataclass
# Not a BaseField as it cannot stand on its own
class MultiCheckboxOption:
    name: str
    region: BoxBounds
    text_region: BoxBounds | None = None


@dataclass
class MultiCheckboxField(BaseField):
    validator: type[MultiCheckboxValidator]
    checkboxes: list[MultiCheckboxOption]


@dataclass
class CheckboxField(BaseField):
    validator: type[SingleCheckboxValidator]
    checkbox_region: BoxBounds


def offset_object(item: object, y_offset: int) -> object | None:
    if isinstance(item, BoxBounds):
        return item._replace(y=item.y + y_offset)
    elif isinstance(item, list):
        return [offset_object(part, y_offset) for part in item if offset_object(part, y_offset) is not None]
    else:
        return None


def create_field_with_offset(field: BaseField, y_offset: int) -> BaseField:
    replacements = {}
    for key, value in vars(field).items():
        # Throw out callables and dunder functions
        if callable(value) or key.startswith('__'):
            continue

        if isinstance(value, BaseField):
            # Recurse to replace the entire object
            replacements[key] = create_field_with_offset(value, y_offset)
        elif isinstance(value, list) and isinstance(value[0], MultiCheckboxOption):
            # Recurse for collections of checkbox options
            # TODO: Handle this automatically for potentially more things that are not lists of MultiCheckboxOption
            replacements[key] = [create_field_with_offset(part, y_offset) for part in value]
        else:
            # Replacements that do not require recursion
            if (new_value := offset_object(value, y_offset)) is not None:
                replacements[key] = new_value

    # Deep copy the object and then perform replacements
    new_field = copy.deepcopy(field)
    for key, value in replacements.items():
        setattr(new_field, key, value)

    return new_field
