from pathlib import Path
from sqlalchemy import types

from src.util.types import BoxBounds


class DbBoxBounds(types.TypeDecorator):
    impl = types.String

    def process_bind_param(self, value: BoxBounds | None, dialect) -> str | None:
        if value is not None:
            assert isinstance(value, BoxBounds), f'Invalid type: {type(value)}'
            value = value.to_db()

        return value

    def process_result_value(self, value: str | None, dialect) -> BoxBounds | None:
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
