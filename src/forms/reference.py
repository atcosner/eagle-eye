from dataclasses import dataclass
from pathlib import Path

from src.definitions.base_fields import BaseField


@dataclass(frozen=True)
class ReferenceForm:
    name: str
    path: Path
    reference_marks_count: int
    regions: dict[str, list[BaseField]]
    default: bool = False

    def __post_init__(self):
        assert self.path.exists(), f'Form path does not exist: {self.path}'
