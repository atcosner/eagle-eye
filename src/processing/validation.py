import logging

from PyQt6.QtNetwork.QHttpHeaders import toListOfPairs

from src.database.fields.multi_checkbox_field import MultiCheckboxField
from src.database.processed_fields.processed_multi_checkbox_option import ProcessedMultiCheckboxOption
from src.database.validation_result import ValidationResult
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
            validation_result = None

    # # Additional validation for checkboxes that need text
    # for checkbox in checkboxes.values():
    #     if checkbox.checked

    # The tooltip assumes failure, overwrite if success
    if validation_result:
        tooltip = f'Field passed validation ({field.validator.name})'

    logger.info(f'Validation: {validation_result}')
    return ValidationResult(
        result=validation_result,
        explanation=tooltip,
    )
