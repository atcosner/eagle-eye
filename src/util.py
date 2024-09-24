import logging

from src.definitions.processed_fields import MultiCheckboxProcessedOption
from src.validation.multi_checkbox import CheckboxOption

UNSAFE_CHARACTERS = ['/', '.', ' ', '%']


def set_up_root_logger(verbose: bool) -> None:
    handler = logging.StreamHandler()
    handler.setFormatter(
        logging.Formatter(
            fmt='{asctime} | {levelname} | {filename} | {message}',
            style='{',
        )
    )

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG if verbose else logging.INFO)
    root_logger.addHandler(handler)


def sanitize_filename(name: str) -> str:
    clean_name = name.lower()
    for character in UNSAFE_CHARACTERS:
        clean_name = clean_name.replace(character, '_')
    return clean_name


def processed_checkbox_to_validate_checkbox(checkbox: MultiCheckboxProcessedOption) -> CheckboxOption:
    return CheckboxOption(
        checked=checkbox.checked,
        text=checkbox.text,
    )
