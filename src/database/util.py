from collections.abc import Iterable
from pathlib import Path
from sqlalchemy import types

from src.util.types import BoxBounds


class DbBoxBounds(types.TypeDecorator):
    # Handles both a single value and a list since the data is simple and not worth adding addition
    # DB complexity (Let's hope I never regret this 😅)
    impl = types.String

    def process_bind_param(self, value: Iterable[BoxBounds] | BoxBounds | None, dialect) -> str | None:
        if value is not None:
            if isinstance(value, BoxBounds):
                value = value.to_db()
            elif isinstance(value, Iterable):
                value = '|'.join([bounds.to_db() for bounds in value])
            else:
                raise TypeError(f'Value was not a BoxBounds or an iterable: {type(value)}')

        return value

    def process_result_value(self, value: str | None, dialect) -> list[BoxBounds] | BoxBounds | None:
        if value is None:
            return value

        if '|' in value:
            return [BoxBounds.from_db(part) for part in value.split('|')]
        else:
            return BoxBounds.from_db(value)


class DbPath(types.TypeDecorator):
    impl = types.String

    def process_bind_param(self, value: Path | None, dialect) -> str | None:
        if value is not None:
            assert isinstance(value, Path), f'Invalid type: {type(value)}'
            value = str(value)

        return value

    def process_result_value(self, value: str | None, dialect) -> BoxBounds | None:
        return Path(value) if value is not None else value
