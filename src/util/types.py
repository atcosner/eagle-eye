from pathlib import Path
from typing import NamedTuple


class BoxBounds(NamedTuple):
    x: int
    y: int
    width: int
    height: int

    def to_db(self) -> str:
        return f'{self.x},{self.y},{self.width},{self.height}'

    @staticmethod
    def from_db(db_value: str | None) -> 'BoxBounds | None':
        return BoxBounds(*(db_value.split(','))) if db_value else None


class InputFileDetails(NamedTuple):
    db_id: int
    path: Path
