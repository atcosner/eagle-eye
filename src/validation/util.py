from typing import NamedTuple
from enum import Enum, auto


class ValidationState(Enum):
    # Success States
    PASSED = auto()
    CORRECTED = auto()  # Initially malformed but passed after corrections
    BYPASS = auto()  # No validation performed

    # Failure States
    MALFORMED = auto()  # Uncorrectable text


VALIDATION_STATE_IMAGE_PATHS = {
    ValidationState.PASSED: '/static/images/passed.png',
    ValidationState.CORRECTED: '/static/images/corrected.png',
    ValidationState.MALFORMED: '/static/images/malformed.png',
    ValidationState.BYPASS: '/static/images/bypass.png',
}

VALIDATION_STATE_BASE_REASONING = {
    ValidationState.PASSED: 'Passed',
    ValidationState.CORRECTED: 'Corrected',
    ValidationState.MALFORMED: 'Malformed Input',
    ValidationState.BYPASS: 'No Validator',
}


class ValidationResult(NamedTuple):
    state: ValidationState
    reasoning: str | None


def get_result_image_path(state: ValidationState) -> str:
    return VALIDATION_STATE_IMAGE_PATHS.get(state, '')


def get_base_reasoning(state: ValidationState) -> str:
    return VALIDATION_STATE_BASE_REASONING.get(state, 'Unknown')
