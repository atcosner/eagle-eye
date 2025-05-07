import logging

from src.database.fields.multi_checkbox_field import MultiCheckboxField
from src.database.fields.multiline_text_field import MultilineTextField
from src.database.fields.text_field import TextField
from src.database.processed_fields.processed_multi_checkbox_option import ProcessedMultiCheckboxOption
from src.database.processed_fields.processed_multiline_text_field import ProcessedMultilineTextField
from src.database.processed_fields.processed_text_field import ProcessedTextField
from src.database.validation.validation_result import ValidationResult
from src.util.validation import MultiCheckboxValidation

logger = logging.getLogger(__name__)


def validate_multi_checkbox_field(
        field: MultiCheckboxField,
        checkboxes: dict[str, ProcessedMultiCheckboxOption],
) -> ValidationResult:
    validation_result: bool | None = None
    tooltip: str | None = None

    match field.validator:
        case MultiCheckboxValidation.NONE:
            validation_result = None
            tooltip = 'No validation defined'
        case MultiCheckboxValidation.REQUIRE_ONE:
            # Ensure that at least one checkbox was checked
            validation_result = any([option.checked for option in checkboxes.values()])
            tooltip = 'This field is required to have at least one option checked'
        case MultiCheckboxValidation.MAXIMUM_ONE:
            # Do not allow more than one option to be checked
            checked_boxes = [option for option in checkboxes.values() if option.checked]
            validation_result = len(checked_boxes) <= 1
            tooltip = f'This field is only allowed to have one option checked, but {len(checked_boxes)} were checked'
        case MultiCheckboxValidation.OPTIONAL:
            # Optional multi-checkboxes always pass validation
            validation_result = True
        case _:
            logger.error(f'Unknown validator: {field.validator.name}')

    # Additional validation for checkboxes that need text
    for checkbox in checkboxes.values():
        if checkbox.checked and checkbox.multi_checkbox_option.text_region is not None:
            if not checkbox.text:
                validation_result = False
                tooltip = 'Checkboxes with text must be filled out'
                break

    # The tooltip assumes failure, overwrite if success
    if validation_result:
        tooltip = f'Field passed validation ({field.validator.name})'

    return ValidationResult(
        result=validation_result,
        explanation=tooltip,
    )


def validate_text_field(
        raw_field: TextField,
        text: str,
) -> ValidationResult:
    return ValidationResult(
        result=None,
        explanation=None,
    )


def validate_multiline_text_field(
        raw_field: MultilineTextField,
        text: str,
) -> ValidationResult:
    return ValidationResult(
        result=None,
        explanation=None,
    )
