from typing import NamedTuple


class BoxBounds(NamedTuple):
    x: int
    y: int
    width: int
    height: int


def get_checkbox_html(form_name: str, checkbox_name: str, checked: bool) -> str:
    checked_str = 'checked' if checked else ''
    return f'<input type="checkbox" name="{form_name}" value="{checkbox_name}" {checked_str}/>'
