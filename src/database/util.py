from collections.abc import Iterable
from pathlib import Path
from sqlalchemy import types

from src.util.types import BoxBounds


class DbBoxBounds(types.TypeDecorator):
    impl = types.String

    def process_bind_param(self, value: BoxBounds | None, dialect) -> str | None:
        if value is not None:
            if isinstance(value, BoxBounds):
                value = value.to_db()
            else:
                raise TypeError(f'Value was not a BoxBounds: {type(value)}')

        return value

    def process_result_value(self, value: str | None, dialect) -> BoxBounds | None:
        return value if value is None else BoxBounds.from_db(value)


class ListDbBoxBounds(types.TypeDecorator):
    impl = types.String

    def process_bind_param(self, value: Iterable[BoxBounds] | None, dialect) -> str | None:
        if value is not None:
            if isinstance(value, Iterable):
                value = '|'.join([bounds.to_db() for bounds in value])
            else:
                raise TypeError(f'Value was not a iterable: {type(value)}')

        return value

    def process_result_value(self, value: str | None, dialect) -> list[BoxBounds] | None:
        return value if value is None else [BoxBounds.from_db(part) for part in value.split('|')]


class DbPath(types.TypeDecorator):
    impl = types.String

    def process_bind_param(self, value: Path | None, dialect) -> str | None:
        if value is not None:
            assert isinstance(value, Path), f'Invalid type: {type(value)}'
            value = str(value)

        return value

    def process_result_value(self, value: str | None, dialect) -> BoxBounds | None:
        return Path(value) if value is not None else value
