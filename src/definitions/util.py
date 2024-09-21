from enum import Enum, auto
from typing import NamedTuple


class BoxBounds(NamedTuple):
    x: int
    y: int
    width: int
    height: int


def get_checkbox_html(name: str, value: str, checked: bool) -> str:
    checked_str = 'checked' if checked else ''
    return f'<input type="checkbox" name="{name}" value="{value}" {checked_str}/>'


class ValidationResult(Enum):
    # Success States
    PASSED = auto()
    CORRECTED = auto()  # Initially malformed but would pass after corrections

    # Failure States
    MALFORMED = auto()  # Uncorrectable text

    # Neutral States
    NO_INPUT = auto()  # No input to validate
    BYPASS = auto()  # No validator specified


RESULT_IMAGE_PATHS = {
    ValidationResult.PASSED: '/static/images/passed.png',
    ValidationResult.CORRECTED: '/static/images/corrected.png',
    ValidationResult.MALFORMED: '/static/images/malformed.png',
    ValidationResult.NO_INPUT: '/static/images/bypass.png',  # TODO: Separate image for this?
    ValidationResult.BYPASS: '/static/images/bypass.png',
}


def get_result_image_path(result: ValidationResult) -> str:
    return RESULT_IMAGE_PATHS.get(result, '')
