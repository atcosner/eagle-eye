from .base import Validator
from .util import ValidationState, ValidationResult


class SingleCheckboxValidator(Validator):
    @staticmethod
    def validate(checked: bool) -> ValidationResult:
        raise NotImplementedError('SingleCheckboxValidator.validate must be overwritten')


class OptionalCheckbox(SingleCheckboxValidator):
    @staticmethod
    def validate(checked: bool) -> ValidationResult:
        return ValidationResult(state=ValidationState.PASSED, reasoning=None)
