import calendar
import datetime
import logging
import re
from rapidfuzz import process, fuzz, utils

from .base import Validator
from .util import ValidationState, ValidationResult

logger = logging.getLogger(__name__)


class TextValidator(Validator):
    @staticmethod
    def validate(text: str) -> ValidationResult:
        raise NotImplementedError('TextValidator.validate must be overwritten')

    @staticmethod
    def export(base_column_name: str, text: str) -> dict[str, str]:
        column_name = base_column_name.lower().replace(' ', '_')
        return {column_name: text.lower()}


class TextValidationBypass(TextValidator):
    @staticmethod
    def validate(text: str) -> ValidationResult:
        return ValidationResult(state=ValidationState.BYPASS, reasoning=None)


class TextRequired(TextValidator):
    @staticmethod
    def validate(text: str) -> ValidationResult:
        if text.strip():
            return ValidationResult(state=ValidationState.PASSED, reasoning=None)
        else:
            return ValidationResult(state=ValidationState.MALFORMED, reasoning='Field cannot be blank')


class IntegerOrFloat(TextValidator):
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
                return ValidationResult(
                    state=ValidationState.MALFORMED,
                    reasoning='Field must be an integer or a float',
                )


class Integer(TextValidator):
    @staticmethod
    def validate(text: str) -> ValidationResult:
        cleaned_text = text.strip()
        if not cleaned_text:
            return ValidationResult(state=ValidationState.MALFORMED, reasoning='Field cannot be blank')

        try:
            int(cleaned_text)
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

    @staticmethod
    def export(base_column_name: str, text: str) -> dict[str, str]:
        return {'KT_number': f'KT_{text}'}


class PrepNumber(TextValidator):
    @staticmethod
    def validate(text: str) -> ValidationResult:
        cleaned_text = text.strip().upper()

        if not cleaned_text:
            return ValidationResult(state=ValidationState.MALFORMED, reasoning='Prep Number cannot be blank')

        # Format: 2-4 capital letters followed by number with 3-5 digits
        if re.compile(r'^[A-Z]{2,4} [0-9]{3,5}$').match(cleaned_text) is not None:
            return ValidationResult(state=ValidationState.PASSED, reasoning=None)
        else:
            return ValidationResult(
                state=ValidationState.MALFORMED,
                reasoning='Prep Number must be 2-4 capital letters followed by a number with 3-5 digits',
            )

    @staticmethod
    def export(base_column_name: str, text: str) -> dict[str, str]:
        formatted_text = text.strip().upper().replace(' ', '_')
        return {'prep_number': formatted_text}


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

    @staticmethod
    def export(base_column_name: str, text: str) -> dict[str, str]:
        # TODO: Should this be exported?
        return {}


class Locality(TextValidator):
    @staticmethod
    def validate(text: str) -> ValidationResult:
        cleaned_text = text.replace(';', ':').strip()

        if not cleaned_text:
            return ValidationResult(state=ValidationState.MALFORMED, reasoning='Locality cannot be blank')

        pattern = re.compile(
            r"^(?P<state>[a-zA-Z-]{2,}(?:[ ,-]+[a-zA-Z-]{2,})*)"
            r" ?: ?(?P<county>[a-zA-Z-]{2,}(?:[ ,-]+[a-zA-Z-]{2,})*)"
            r" ?: ?(?P<location>[a-zA-Z-]{2,}(?:[ ,-]+[a-zA-Z-]{2,})*)$"
        )

        # Format: <STATE> : <COUNTY> : <PLACE>
        if (match := pattern.match(cleaned_text)) is not None:
            formatted_text = f'{match.group("state")} : {match.group("county")} : {match.group("location")}'
            return ValidationResult(
                state=ValidationState.PASSED if formatted_text == cleaned_text else ValidationState.CORRECTED,
                reasoning=None,
                correction=formatted_text,
            )
        else:
            return ValidationResult(
                state=ValidationState.MALFORMED,
                reasoning='Locality must be in the format: [STATE] : [COUNTY] : [PLACE]',
            )

    @staticmethod
    def export(base_column_name: str, text: str) -> dict[str, str]:
        formatted_text = text.strip()
        return {
            'country': 'USA',
            'locality_string': formatted_text,
        }


class Species(TextValidator):
    @staticmethod
    def validate(text: str) -> ValidationResult:
        cleaned_text = text.strip()

        # TODO: Check the species against a offline list

    @staticmethod
    def export(base_column_name: str, text: str) -> dict[str, str]:
        formatted_text = text.strip()
        return {
            'genus': 'USA',
            'species': formatted_text,
        }


class GpsCoordinatePoint(TextValidator):
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


class GpsWaypoint(TextValidator):
    @staticmethod
    def validate(text: str) -> ValidationResult:
        cleaned_text = text.strip()

        # Waypoint can be blank (form has exact coordinates)
        if not cleaned_text:
            return ValidationResult(state=ValidationState.PASSED, reasoning=None)

        if re.compile(r'^[a-zA-Z0-9]{4,}$').match(cleaned_text) is not None:
            return ValidationResult(state=ValidationState.PASSED, reasoning=None)
        else:
            return ValidationResult(
                state=ValidationState.MALFORMED,
                reasoning='GPS waypoints must be a string of letters and then numbers',
            )

    @staticmethod
    def export(base_column_name: str, text: str) -> dict[str, str]:
        # Data should be exported as "<LETTERS>_<NUMBERS>"
        formatted_text = text
        for idx, char in enumerate(text):
            # Find the first number and split on that location
            if char.isnumeric():
                formatted_text = f'{text[:idx]}_{text[idx:]}'
                break

        return {'gps_wp': formatted_text}


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

        # Attempt to correct the month if it did not match
        made_correction = False
        if month not in calendar.month_name:
            match, ratio, edits = process.extractOne(
                month,
                calendar.month_name,
                scorer=fuzz.WRatio,
                processor=utils.default_process,
            )
            logger.info(f'Found match: "{match}", ratio: {ratio}, edits: {edits}')
            if ratio > 65:
                made_correction = True
                month = match.capitalize()

        # Enforce constraints on values
        day_match = 1 <= day <= 31
        month_match = month in calendar.month_name
        year_match = 2024 <= year <= datetime.datetime.now().year

        if day_match and month_match and year_match:
            return ValidationResult(
                state=ValidationState.CORRECTED if made_correction else ValidationState.PASSED,
                reasoning=None,
                correction=f'{day} {month} {year}'
            )
        else:
            return ValidationResult(
                state=ValidationState.MALFORMED,
                reasoning=f'Value outside acceptable values (Day: {day}, Month: {month}, Year: {year})',
            )

    @staticmethod
    def export(base_column_name: str, text: str) -> dict[str, str]:
        column_name = base_column_name.replace('Date', '').strip().lower()

        text_parts = [part.strip() for part in text.strip().split(' ')]
        if len(text_parts) != 3:
            text_parts = [text, text, text]

        return {
            f'{column_name}_year':  text_parts[2],
            f'{column_name}_month': text_parts[1],
            f'{column_name}_day': text_parts[0],
        }


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
            formatted_text = f'{hour:02}:{minute:02}'
            return ValidationResult(
                state=ValidationState.PASSED if formatted_text == cleaned_text else ValidationState.CORRECTED,
                reasoning=None,
                correction=formatted_text,
            )
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

        if re.compile(r'^[A-Z]{2,4}$').match(cleaned_text) is not None:
            return ValidationResult(state=ValidationState.PASSED, reasoning=None)
        else:
            return ValidationResult(
                state=ValidationState.MALFORMED,
                reasoning='Initials must be 2-4 capital letters',
            )

    @staticmethod
    def export(base_column_name: str, text: str) -> dict[str, str]:
        return {f'{base_column_name.lower()}_init': text.strip()}


class Habitat(TextValidator):
    @staticmethod
    def validate(text: str) -> ValidationResult:
        if text.strip():
            return ValidationResult(state=ValidationState.PASSED, reasoning=None)
        else:
            return ValidationResult(state=ValidationState.MALFORMED, reasoning='Field cannot be blank')

    @staticmethod
    def export(base_column_name: str, text: str) -> dict[str, str]:
        return {base_column_name.lower(): text.lower()}


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
