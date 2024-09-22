from dataclasses import dataclass
from pathlib import Path

from .fields import TextField


@dataclass
class ParsedField:
    name: str
    roi_image_path: Path


@dataclass
class ParsedTextField(ParsedField):
    field: TextField
    text: str
