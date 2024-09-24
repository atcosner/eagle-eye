from abc import ABC, abstractmethod
from typing import Any

from .util import ValidationState, ValidationResult


class Validator(ABC):
    @staticmethod
    @abstractmethod
    def validate(value: Any) -> ValidationResult:
        ...


class NoValidation(Validator):
    @staticmethod
    def validate(value: Any) -> ValidationResult:
        return ValidationResult(state=ValidationState.BYPASS, reasoning=None)
