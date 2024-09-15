import re
from abc import ABC, abstractmethod
from enum import Enum, auto


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


class Validator(ABC):
    @staticmethod
    @abstractmethod
    def validate(text: str) -> tuple[ValidationResult, str]:
        ...

    @staticmethod
    @abstractmethod
    def export(text: str) -> str:
        # TODO: Should this re-validate the string?
        #  It could pass from OCR and then fail if the user edits it or vice versa
        ...


class NoValidation(Validator):
    @staticmethod
    def validate(text: str) -> tuple[ValidationResult, str]:
        return ValidationResult.BYPASS, text

    @staticmethod
    def export(text: str) -> str:
        return text


class KtNumber(Validator):
    @staticmethod
    def validate(text: str) -> tuple[ValidationResult, str]:
        if not text:
            return ValidationResult.NO_INPUT, text

        # KT Numbers are expected to be exactly 5 numbers
        if re.compile(r'^[0-9]{5}$').match(text) is not None:
            return ValidationResult.PASSED, text
        else:
            # TODO: Is there a way to correct bad input?
            return ValidationResult.MALFORMED, text

    @staticmethod
    def export(text: str) -> str:
        return f'KT_{text}'


class PrepNumber(Validator):
    @staticmethod
    def validate(text: str) -> tuple[ValidationResult, str]:
        if not text:
            return ValidationResult.NO_INPUT, text

        # Format: 3 capital letters followed by number
        if re.compile(r'^[A-Z]{3} [0-9]+$').match(text) is not None:
            return ValidationResult.PASSED, text
        else:
            # TODO: Should we just upper() here?
            #  Capital I might OCR as lowercase l ?
            return ValidationResult.MALFORMED, text

    @staticmethod
    def export(text: str) -> str:
        # TODO: Export format?
        return text
