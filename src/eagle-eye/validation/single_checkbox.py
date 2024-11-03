from .base import Validator
from .util import ValidationState, ValidationResult, export_bool_to_string


class SingleCheckboxValidator(Validator):
    @staticmethod
    def validate(checked: bool) -> ValidationResult:
        raise NotImplementedError('SingleCheckboxValidator.validate must be overwritten')

    @staticmethod
    def export(base_column_name: str, checked: bool) -> dict[str, str]:
        column_name = base_column_name.lower().replace(' ', '_')
        return {column_name: export_bool_to_string(checked)}


class OptionalCheckbox(SingleCheckboxValidator):
    @staticmethod
    def validate(checked: bool) -> ValidationResult:
        return ValidationResult(state=ValidationState.PASSED, reasoning=None)
