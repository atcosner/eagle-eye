from dataclasses import dataclass
from pathlib import Path

from .fields import BaseField


@dataclass
class ParsedField:
    raw_field: BaseField
    roi_image_path: Path


@dataclass
class ParsedTextField(ParsedField):
    text: str
