import calendar
import datetime
import re
from abc import ABC, abstractmethod
from typing import Any

from .util import ValidationResult


class Validator(ABC):
    @staticmethod
    @abstractmethod
    def validate(result, allow_correction: bool) -> ValidationResult:
        ...


class NoValidation(Validator):
    @staticmethod
    def validate(result, allow_correction: bool) -> ValidationResult:
        return ValidationResult.BYPASS


class KtNumber(Validator):
    @staticmethod
    def validate(result, allow_correction: bool) -> ValidationResult:
        if not text:
            return ValidationResult.NO_INPUT, text

        # KT Numbers are expected to be exactly 5 numbers
        if re.compile(r'^[0-9]{5}$').match(text) is not None:
            return ValidationResult.PASSED, text
        else:
            # TODO: Is there a way to correct bad input?
            return ValidationResult.MALFORMED, text


class PrepNumber(Validator):
    @staticmethod
    def validate(text: str, allow_correction: bool) -> ValidationResult:
        if not text:
            return ValidationResult.NO_INPUT, text

        # Format: 2-4 capital letters followed by number with unlimited digits
        if re.compile(r'^[A-Z]{2,4} [0-9]{3,}$').match(text) is not None:
            return ValidationResult.PASSED, text
        else:
            # TODO: Should we just upper() here?
            #  Capital I might OCR as lowercase l?
            return ValidationResult.MALFORMED, text


class Locality(Validator):
    @staticmethod
    def validate(text: str, allow_correction: bool) -> ValidationResult:
        if not text:
            return ValidationResult.NO_INPUT, text

        # Pre-processing
        cleaned_text = text.replace(';', ':').strip()
        pattern = re.compile(
            r"^(?P<state>[a-zA-Z-]{2,}(?: [a-zA-Z-]{2,})*)"
            r" ?: ?(?P<county>[a-zA-Z-]{2,}(?: [a-zA-Z-]{2,})*)"
            r" ?: ?(?P<location>[a-zA-Z-]{2,}(?: [a-zA-Z-]{2,})*)$"
        )

        # Format: <STATE> : <COUNTY> : <PLACE>
        if (match := pattern.match(cleaned_text)) is not None:
            formatted_text = f'{match.group("state")} : {match.group("county")} : {match.group("location")}'
            return ValidationResult.PASSED, formatted_text
        else:
            return ValidationResult.MALFORMED, text


class GpsPoint(Validator):
    @staticmethod
    def validate(text: str, allow_correction: bool) -> ValidationResult:
        if not text:
            return ValidationResult.NO_INPUT, text

        # Pre-processing
        cleaned_text = text.strip()
        pattern = re.compile(r'^[+-]?\d{1,3}.\d{1,8}$')

        # Format: <STATE> : <COUNTY> : <PLACE>
        if pattern.match(cleaned_text) is not None:
            return ValidationResult.PASSED, cleaned_text
        else:
            return ValidationResult.MALFORMED, text


class Date(Validator):
    @staticmethod
    def validate(text: str, allow_correction: bool) -> ValidationResult:
        if not text:
            return ValidationResult.NO_INPUT, text

        # Pre-processing
        cleaned_text = text.strip()

        # Format: <DAY> <MONTH_STRING> <YEAR>
        pattern = re.compile(r'^(?P<day>\d{1,2}) (?P<month>[a-zA-Z]{3,9}) (?P<year>\d{4})$')
        if (match := pattern.match(cleaned_text)) is None:
            return ValidationResult.MALFORMED, text

        # Enforce constraints on values
        day_match = 1 <= int(match.group('day')) <= 31
        month_match = match.group('month').capitalize() in calendar.month_name
        year_match = 2024 <= int(match.group('year')) <= datetime.datetime.now().year

        if day_match and month_match and year_match:
            return ValidationResult.PASSED, cleaned_text
        else:
            return ValidationResult.MALFORMED, text


class Time(Validator):
    @staticmethod
    def validate(text: str, allow_correction: bool) -> ValidationResult:
        if not text:
            return ValidationResult.NO_INPUT, text

        # Pre-processing
        cleaned_text = text.strip()

        # Format: <HOUR> : <MINUTE>
        pattern = re.compile(r'^(?P<hour>\d{1,2}) ?: ?(?P<minute>\d{2})$')
        if (match := pattern.match(cleaned_text)) is None:
            return ValidationResult.MALFORMED, text

        # Enforce constraints on values
        hour_match = 0 <= int(match.group('hour')) <= 23
        minute_match = 0 <= int(match.group('minute')) <= 59

        if hour_match and minute_match:
            return ValidationResult.PASSED, f'{match.group("hour")}:{match.group("minute")}'
        else:
            return ValidationResult.MALFORMED, text
