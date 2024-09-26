import calendar
import datetime
import re

from .base import Validator
from .util import ValidationState, ValidationResult


class TextValidator(Validator):
    @staticmethod
    def validate(text: str) -> ValidationResult:
        raise NotImplementedError('TextValidator.validate must be overwritten')


class TextValidationBypass(TextValidator):
    @staticmethod
    def validate(text: str) -> ValidationResult:
        return ValidationResult(state=ValidationState.BYPASS, reasoning=None)


class TextOptional(TextValidator):
    @staticmethod
    def validate(text: str) -> ValidationResult:
        return ValidationResult(state=ValidationState.PASSED, reasoning=None)


class TextRequired(TextValidator):
    @staticmethod
    def validate(text: str) -> ValidationResult:
        if text.strip():
            return ValidationResult(state=ValidationState.PASSED, reasoning=None)
        else:
            return ValidationResult(state=ValidationState.MALFORMED, reasoning='Field cannot be blank')


class Number(TextValidator):
    @staticmethod
    def validate(text: str) -> ValidationResult:
        cleaned_text = text.strip()
        if not cleaned_text:
            return ValidationResult(state=ValidationState.MALFORMED, reasoning='Field cannot be blank')

        try:
            int(cleaned_text)
            return ValidationResult(state=ValidationState.PASSED, reasoning=None)
        except ValueError:
            try:
                float(cleaned_text)
                return ValidationResult(state=ValidationState.PASSED, reasoning=None)
            except ValueError:
                return ValidationResult(state=ValidationState.MALFORMED, reasoning='Field must be a number')


class KtNumber(TextValidator):
    @staticmethod
    def validate(text: str) -> ValidationResult:
        cleaned_text = text.strip()

        if not cleaned_text:
            return ValidationResult(state=ValidationState.MALFORMED, reasoning='KT Number cannot be blank')

        # KT Numbers are expected to be exactly 5 numbers
        if re.compile(r'^[0-9]{5}$').match(cleaned_text) is not None:
            return ValidationResult(state=ValidationState.PASSED, reasoning=None)
        else:
            # TODO: Is there a way to correct bad input?
            return ValidationResult(state=ValidationState.MALFORMED, reasoning='KT Number must be exactly 5 digits')


class PrepNumber(TextValidator):
    @staticmethod
    def validate(text: str) -> ValidationResult:
        cleaned_text = text.strip()

        if not cleaned_text:
            return ValidationResult(state=ValidationState.MALFORMED, reasoning='Prep Number cannot be blank')

        # Format: 2-4 capital letters followed by number with 3+ digits
        if re.compile(r'^[A-Z]{2,4} [0-9]{3,}$').match(cleaned_text) is not None:
            return ValidationResult(state=ValidationState.PASSED, reasoning=None)
        else:
            # TODO: Should we just upper() here?
            #  Capital I might OCR as lowercase l?
            return ValidationResult(
                state=ValidationState.MALFORMED,
                reasoning='Prep Number must be 2-4 capital letters followed by a number with 3+ digits',
            )


class OtNumber(TextValidator):
    @staticmethod
    def validate(text: str) -> ValidationResult:
        cleaned_text = text.strip()

        if not cleaned_text:
            return ValidationResult(state=ValidationState.MALFORMED, reasoning='OT Number cannot be blank')

        # OT Number: <YEAR>-<NUMBER>
        if re.compile(r'^\d{4}-\d+$').match(cleaned_text) is not None:
            return ValidationResult(state=ValidationState.PASSED, reasoning=None)
        else:
            return ValidationResult(
                state=ValidationState.MALFORMED,
                reasoning='OT Number must be in the format: <YEAR>-<NUMBER>',
            )


class Locality(TextValidator):
    @staticmethod
    def validate(text: str) -> ValidationResult:
        cleaned_text = text.replace(';', ':').strip()

        if not cleaned_text:
            return ValidationResult(state=ValidationState.MALFORMED, reasoning='Locality cannot be blank')

        pattern = re.compile(
            r"^(?P<state>[a-zA-Z-]{2,}(?: [a-zA-Z-]{2,})*)"
            r" ?: ?(?P<county>[a-zA-Z-]{2,}(?: [a-zA-Z-]{2,})*)"
            r" ?: ?(?P<location>[a-zA-Z-]{2,}(?: [a-zA-Z-]{2,})*)$"
        )

        # Format: <STATE> : <COUNTY> : <PLACE>
        if (match := pattern.match(cleaned_text)) is not None:
            # formatted_text = f'{match.group("state")} : {match.group("county")} : {match.group("location")}'
            return ValidationResult(state=ValidationState.PASSED, reasoning=None)
        else:
            return ValidationResult(
                state=ValidationState.MALFORMED,
                reasoning='Locality must be in the format: [STATE] : [COUNTY] : [PLACE]',
            )


class GpsPoint(TextValidator):
    @staticmethod
    def validate(text: str) -> ValidationResult:
        cleaned_text = text.strip()

        # GPS points can be blank
        if not cleaned_text:
            return ValidationResult(state=ValidationState.PASSED, reasoning=None)

        if re.compile(r'^[+-]?\d{1,3}.\d{4,8}$').match(cleaned_text) is not None:
            return ValidationResult(state=ValidationState.PASSED, reasoning=None)
        else:
            return ValidationResult(
                state=ValidationState.MALFORMED,
                reasoning='GPS points must be in DD format (Min 4 decimal places)',
            )


class Date(TextValidator):
    @staticmethod
    def validate(text: str) -> ValidationResult:
        cleaned_text = text.strip()

        if not text:
            return ValidationResult(state=ValidationState.MALFORMED, reasoning='Date field cannot be blank')

        # Format: <DAY> <MONTH_STRING> <YEAR>
        pattern = re.compile(r'^(?P<day>\d{1,2}) (?P<month>[a-zA-Z]{3,9}) (?P<year>\d{4})$')
        if (match := pattern.match(cleaned_text)) is None:
            return ValidationResult(
                state=ValidationState.MALFORMED,
                reasoning='Dates must be in the format: [Day] [Month Name] [Year]',
            )

        # Match groups
        day = int(match.group('day'))
        month = match.group('month').capitalize()
        year = int(match.group('year'))

        # Enforce constraints on values
        day_match = 1 <= day <= 31
        month_match = month in calendar.month_name
        year_match = 2024 <= year <= datetime.datetime.now().year

        if day_match and month_match and year_match:
            return ValidationResult(state=ValidationState.PASSED, reasoning=None)
        else:
            return ValidationResult(
                state=ValidationState.MALFORMED,
                reasoning=f'Value outside acceptable values (Day: {day}, Month: {month}, Year: {year})',
            )


class Time(TextValidator):
    @staticmethod
    def validate(text: str) -> ValidationResult:
        cleaned_text = text.strip()

        if not text:
            return ValidationResult(state=ValidationState.MALFORMED, reasoning='Time field cannot be blank')

        # Format: <HOUR> : <MINUTE>
        pattern = re.compile(r'^(?P<hour>\d{1,2}) ?: ?(?P<minute>\d{2})$')
        if (match := pattern.match(cleaned_text)) is None:
            return ValidationResult(
                state=ValidationState.MALFORMED,
                reasoning='Times must be in the format: [Hour]:[Minute]',
            )

        # Match groups
        hour = int(match.group('hour'))
        minute = int(match.group('minute'))

        # Enforce constraints on values
        hour_match = 0 <= hour <= 23
        minute_match = 0 <= minute <= 59

        if hour_match and minute_match:
            return ValidationResult(state=ValidationState.PASSED, reasoning=None)
        else:
            return ValidationResult(
                state=ValidationState.MALFORMED,
                reasoning=f'Value outside acceptable values (Hour: {hour}, Minute: {minute})',
            )


class Initials(TextValidator):
    @staticmethod
    def validate(text: str) -> ValidationResult:
        cleaned_text = text.strip()

        if not cleaned_text:
            return ValidationResult(state=ValidationState.MALFORMED, reasoning='Field cannot be blank')

        if re.compile(r'^[A-Z]{3,4}$').match(cleaned_text) is not None:
            return ValidationResult(state=ValidationState.PASSED, reasoning=None)
        else:
            return ValidationResult(
                state=ValidationState.MALFORMED,
                reasoning='Initials must be 3-4 capital letters',
            )


class Tissues(TextValidator):
    @staticmethod
    def validate(text: str) -> ValidationResult:
        valid_characters = ['M', 'L', 'G', 'H']
        cleaned_text = text.strip()

        if not cleaned_text:
            return ValidationResult(state=ValidationState.MALFORMED, reasoning='Field cannot be blank')

        parts = [part.strip() for part in cleaned_text.split(',')]
        length_check = all([len(part) == 1 for part in parts])
        character_check = all([part in valid_characters for part in parts])

        if length_check and character_check:
            return ValidationResult(state=ValidationState.PASSED, reasoning=None)
        else:
            return ValidationResult(
                state=ValidationState.MALFORMED,
                reasoning=f'Tissues must be a CSV of valid characters (Valid: {valid_characters})',
            )
