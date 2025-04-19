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
        if db_value is None:
            return None

        int_values = [int(part) for part in db_value.split(',')]
        return BoxBounds(*int_values)


class FileDetails(NamedTuple):
    db_id: int
    path: Path
