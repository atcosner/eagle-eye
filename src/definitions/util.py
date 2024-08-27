from typing import NamedTuple


class BoxBounds(NamedTuple):
    # Top Left Coordinate
    x: int
    y: int
    width: int
    height: int


class TextField(NamedTuple):
    name: str
    region: BoxBounds
    segment_option: str = '7'  # Specific to Tesseract (https://tesseract-ocr.github.io/tessdoc/ImproveQuality.html#page-segmentation-method)


class CheckboxOptionField(NamedTuple):
    name: str
    region: BoxBounds
    text_region: BoxBounds | None = None


class CheckboxMultiField(NamedTuple):
    name: str
    visual_region: BoxBounds
    options: list[CheckboxOptionField]


FormField = TextField | CheckboxMultiField
