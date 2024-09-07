from typing import NamedTuple

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


FormField = TextField | MultilineTextField | TextFieldOrCheckbox | MultiCheckboxField | CheckboxField
