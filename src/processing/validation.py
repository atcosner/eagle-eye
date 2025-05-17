import logging
import re
from typing import Iterable

from PyQt6.QtCore import QDate, QTime

from src.database.fields.multi_checkbox_field import MultiCheckboxField
from src.database.fields.text_field import TextField
from src.database.processed_fields.processed_multi_checkbox_option import ProcessedMultiCheckboxOption
from src.database.validation.text_validator import TextValidator
from src.database.validation.validation_result import ValidationResult
from src.util.validation import (
    MultiCheckboxValidation,
    TextValidatorDatatype,
    VALID_TIME_FORMATS,
    VALID_DATE_FORMATS,
    find_best_string_match,
)

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


def get_explanation(validator: TextValidator, reason: str) -> str:
    return reason if validator.error_tooltip is None else validator.error_tooltip


def check_conversion_from_string(obj: type[QTime | QDate], formats: Iterable[str], text: str) -> bool:
    match_found = False
    for str_format in formats:
        time = obj.fromString(text, str_format)
        if time.isValid():
            match_found = True
            break

    return match_found


def validate_raw_text(validator: TextValidator, text: str) -> ValidationResult:
    # Check if there is any validation to do
    if validator.text_regex is None:
        return ValidationResult(result=None, explanation=None)

    regex_pattern = re.compile(validator.text_regex)
    regex_match = regex_pattern.match(text)
    if regex_match is None:
        return ValidationResult(
            result=False,
            explanation=get_explanation(
                validator,
                f'Text did not match the regular expression\n{validator.text_regex}',
            ),
        )

    # Check if we should reformat
    if validator.reformat_regex is None:
        return ValidationResult(result=True, explanation=None)

    # Reformat the text
    regex_group_names = list(regex_pattern.groupindex.keys())
    # TODO: Change this to debug level
    logger.info(f'Found {len(regex_group_names)} groups in the regex: {regex_group_names}')

    groups = {group_name: regex_match.group(group_name) for group_name in regex_group_names}
    reformatted_text = validator.reformat_regex.format(**groups)

    return ValidationResult(result=True, explanation=None, correction=reformatted_text)


def validate_text_field(
        raw_field: TextField,
        text: str,
        force_fail: bool = False,
        allow_fuzzy: bool = False,
) -> ValidationResult:
    validator = raw_field.text_validator
    if validator is None:
        return ValidationResult(result=None, explanation=None)

    if force_fail:
        return ValidationResult(
            result=False,
            explanation='Data was in an invalid format',
        )

    if not text:
        if validator.text_required:
            return ValidationResult(
                result=False,
                explanation='Field cannot be blank',
            )
        else:
            return ValidationResult(result=True, explanation=None)

    # Validate each different type of data separately
    text = text.strip()
    if validator.datatype is TextValidatorDatatype.RAW_TEXT:
        return validate_raw_text(validator, text)

    elif validator.datatype is TextValidatorDatatype.DATE:
        if check_conversion_from_string(QDate, VALID_DATE_FORMATS, text):
            return ValidationResult(result=True, explanation=None)
        else:
            return ValidationResult(
                result=False,
                explanation=get_explanation(validator, 'Field could not be interpreted as a date'),
            )

    elif validator.datatype is TextValidatorDatatype.TIME:
        if check_conversion_from_string(QTime, VALID_TIME_FORMATS, text):
            return ValidationResult(result=True, explanation=None)
        else:
            return ValidationResult(
                result=False,
                explanation=get_explanation(validator, 'Field could not be interpreted as a time'),
            )

    elif validator.datatype is TextValidatorDatatype.INTEGER:
        try:
            int(text)
            return ValidationResult(result=True, explanation=None)
        except ValueError:
            return ValidationResult(
                result=False,
                explanation=get_explanation(validator, 'Field must be an integer'),
            )

    elif validator.datatype is TextValidatorDatatype.INTEGER_OR_FLOAT:
        try:
            int(text)
            return ValidationResult(result=True, explanation=None)
        except ValueError:
            try:
                float(text)
                return ValidationResult(result=True, explanation=None)
            except ValueError:
                return ValidationResult(
                    result=False,
                    explanation=get_explanation(validator, 'Field must be an integer or a float'),
                )

    elif validator.datatype is TextValidatorDatatype.LIST_CHOICE:
        possible_choices = [x.text for x in validator.text_choices]
        if text in possible_choices:
            return ValidationResult(result=True, explanation=None)
        else:
            # See if we are allowed to find the closest match
            if allow_fuzzy and validator.allow_closest_match_correction:
                match = find_best_string_match(text, possible_choices)
                if match is not None:
                    return ValidationResult(
                        result=True,
                        explanation=f'Correction made: "{text}" -> "{match}"',
                        correction=match,
                    )

            return ValidationResult(
                result=False,
                explanation=get_explanation(validator, f'Value "{text}" not in the possible choices'),
            )

    elif validator.datatype is TextValidatorDatatype.CSV_OF_CHOICE:
        possible_choices = [x.text for x in validator.text_choices]
        entries = [entry.strip() for entry in text.split(',')]

        for entry in entries:
            if entry not in possible_choices:
                return ValidationResult(
                    result=False,
                    explanation=get_explanation(validator, f'Value "{entry}" not in the possible choices'),
                )

        # Offer a correction with whitespace stripped
        correction: str | None = None
        reformatted_text = ','.join(entries)
        if reformatted_text != text:
            correction = reformatted_text

        return ValidationResult(result=True, explanation=None, correction=correction)

    elif validator.datatype is TextValidatorDatatype.GPS_POINT_DD:
        if re.compile(r'^[+-]?\d{1,3}.\d{4,8}$').match(text) is not None:
            return ValidationResult(result=True, explanation=None)
        else:
            return ValidationResult(
                result=False,
                explanation=get_explanation(
                    validator,
                    'GPS points must be in decimal degrees format (Min 4 decimal places)',
                ),
            )

    elif validator.datatype is TextValidatorDatatype.KU_GPS_WAYPOINT:
        if re.compile(r'^[a-zA-Z0-9]{4,}$').match(text) is not None:
            return ValidationResult(result=True, explanation=None)
        else:
            return ValidationResult(
                result=False,
                explanation=get_explanation(
                    validator,
                    'GPS waypoints must be a string of letters and then numbers',
                ),
            )

    return ValidationResult(result=None, explanation=None)
