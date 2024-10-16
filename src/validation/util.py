import logging

from enum import Enum, auto
from pathlib import Path
from rapidfuzz import process, fuzz, utils
from typing import Any, NamedTuple, Iterable

logger = logging.getLogger(__name__)

_ORNITHOLOGY_SPECIES_FILE = Path(__file__).parent / 'NACC_list_species.csv'


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
    correction: Any | None = None


def get_result_image_path(state: ValidationState) -> str:
    return VALIDATION_STATE_IMAGE_PATHS.get(state, '')


def get_base_reasoning(state: ValidationState) -> str:
    return VALIDATION_STATE_BASE_REASONING.get(state, 'Unknown')


def export_bool_to_string(value: bool) -> str:
    return 'yes' if value else 'no'


def _read_species_list(file_path: Path) -> list[str]:
    with file_path.open('r') as file:
        return [line.lower() for line in file.readlines()]


# Read in the list of species on import
ORNITHOLOGY_SPECIES_LIST = _read_species_list(_ORNITHOLOGY_SPECIES_FILE)


def find_best_string_match(text: str, options: Iterable[str]) -> tuple[bool, str]:
    match, ratio, edits = process.extractOne(
        text,
        options,
        scorer=fuzz.WRatio,
        processor=utils.default_process,
    )
    logger.info(f'Best match: "{text}" -> "{match}", ratio: {ratio}, edits: {edits}')
    return (True, match) if ratio > 65 else (False, text)
