from typing import NamedTuple


class BoxBounds(NamedTuple):
    x: int
    y: int
    width: int
    height: int


def get_checkbox_html(name: str, value: str, checked: bool) -> str:
    checked_str = 'checked' if checked else ''
    return f'<input type="checkbox" name="{name}" value="{value}" {checked_str}/>'
