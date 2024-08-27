import logging
from dataclasses import dataclass
from pathlib import Path

from .definitions.util import CheckboxOptionField

UNSAFE_CHARACTERS = ['/', '.', ' ']


def set_up_root_logger(verbose: bool) -> None:
    handler = logging.StreamHandler()
    handler.setFormatter(
        logging.Formatter(
            fmt='{asctime} | {levelname} | {filename} | {message}',
            style='{',
        )
    )

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG if verbose else logging.WARNING)
    root_logger.addHandler(handler)


def sanitize_filename(name: str) -> str:
    clean_name = name.lower()
    for character in UNSAFE_CHARACTERS:
        clean_name = clean_name.replace(character, '_')
    return clean_name


@dataclass
class OcrResult:
    field_name: str
    roi_image_path: Path
    extracted_text: str
    user_correction: str | None = None

    def get_text(self) -> str:
        return self.user_correction if self.user_correction is not None else self.extracted_text

    def get_html_input(self) -> str:
        return f'''
            <input type="text" name="{self.field_name}" class="corrections-box" value="{self.get_text()}"/>
        '''.strip()


@dataclass
class CheckboxResult:
    field_name: str
    roi_image_path: Path
    selected_option: str | None
    user_correction: str | None = None

    def get_text(self) -> str:
        if self.user_correction is not None:
            return self.user_correction
        else:
            return self.selected_option if self.selected_option is not None else ''

    def get_html_input(self) -> str:
        return f'''
            <input type="text" name="{self.field_name}" class="corrections-box" value="{self.get_text()}"/>
        '''.lstrip()


FieldResult = OcrResult | CheckboxResult
