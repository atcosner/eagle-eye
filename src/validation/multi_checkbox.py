from typing import NamedTuple

from .base import Validator
from .util import ValidationState, ValidationResult


class CheckboxOption(NamedTuple):
    checked: bool
    text: str | None


class MultiCheckboxValidator(Validator):
    @staticmethod
    def validate(checkboxes: list[CheckboxOption]) -> ValidationResult:
        raise NotImplementedError('MultiCheckboxValidator.validate must be overwritten')


class OptionalCheckboxes(MultiCheckboxValidator):
    @staticmethod
    def validate(checkboxes: list[CheckboxOption]) -> ValidationResult:
        return ValidationResult(state=ValidationState.PASSED, reasoning=None)


class RequireOneCheckboxes(MultiCheckboxValidator):
    @staticmethod
    def validate(checkboxes: list[CheckboxOption]) -> ValidationResult:
        valid_checked = any([option.checked for option in checkboxes])
        valid_text = True
        for option in checkboxes:
            if option.checked and option.text is not None:
                cleaned_text = option.text.strip()
                if cleaned_text == '':
                    valid_text = False

        if valid_checked and valid_text:
            return ValidationResult(state=ValidationState.PASSED, reasoning=None)
        else:
            error_reasons = []
            if not valid_checked:
                error_reasons.append('At least one checkbox is required')
            if not valid_text:
                error_reasons.append('Checked options with text must be filled out')

            return ValidationResult(
                state=ValidationState.MALFORMED,
                reasoning=','.join(error_reasons),
            )
