from .base import Validator
from .util import ValidationState, ValidationResult, export_bool_to_string

# TODO: Turn this into a named tuple to stop using integer indexing below
CheckboxData = tuple[str, bool, str | None]


class MultiCheckboxValidator(Validator):
    @staticmethod
    def validate(checkboxes: list[CheckboxData]) -> ValidationResult:
        raise NotImplementedError('MultiCheckboxValidator.validate must be overwritten')

    @staticmethod
    def export(base_column_name: str, checkboxes: list[CheckboxData]) -> dict[str, str]:
        columns = {}
        for checkbox in checkboxes:
            column_name = f'{base_column_name}_{checkbox[0]}'.lower().replace(' ', '_')
            # If the checkbox has a text region, use it instead of yes/no
            row_value = checkbox[2] if checkbox[2] is not None else export_bool_to_string(checkbox[1])
            columns[column_name] = row_value

        return columns


class OptionalCheckboxes(MultiCheckboxValidator):
    @staticmethod
    def validate(checkboxes: list[CheckboxData]) -> ValidationResult:
        return ValidationResult(state=ValidationState.PASSED, reasoning=None)


class RequireOneCheckbox(MultiCheckboxValidator):
    @staticmethod
    def validate(checkboxes: list[CheckboxData]) -> ValidationResult:
        valid_checked = any([option[1] for option in checkboxes])
        valid_text = True
        for option in checkboxes:
            if option[1] and option[2] is not None:
                cleaned_text = option[2].strip()
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
                reasoning=', '.join(error_reasons),
            )