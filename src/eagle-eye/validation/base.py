import logging
from abc import ABC, abstractmethod
from typing import Any

from .util import ValidationState, ValidationResult

logger = logging.getLogger(__name__)


class Validator(ABC):
    @staticmethod
    @abstractmethod
    def validate(value: Any) -> ValidationResult:
        ...

    @staticmethod
    @abstractmethod
    def export(base_column_name: str, value: Any) -> dict[str, str]:
        ...


class NoValidation(Validator):
    @staticmethod
    def validate(value: Any) -> ValidationResult:
        return ValidationResult(state=ValidationState.BYPASS, reasoning=None)

    @staticmethod
    def export(base_column_name: str, value: Any) -> dict[str, str]:
        logger.warning('Please define a validator for this field')
        return {base_column_name: str(value)}
