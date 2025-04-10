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
