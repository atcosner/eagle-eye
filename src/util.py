import logging
from dataclasses import dataclass
from pathlib import Path

from .definitions.util import TextField, CheckboxMultiField

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
    field: TextField
    roi_image_path: Path
    extracted_text: str
    user_correction: str | None = None

    def get_text(self) -> str:
        return self.user_correction if self.user_correction is not None else self.extracted_text

    def handle_no_correction(self) -> None:
        # Text fields always come back on HTML forms
        pass

    def set_correction(self, correction: str) -> None:
        if self.extracted_text != correction:
            self.user_correction = correction

    def get_html_input(self) -> str:
        return f'''
            <input type="text" name="{self.field_name}" class="corrections-box" value="{self.get_text()}"/>
        '''


@dataclass
class CheckboxResult:
    field_name: str
    field: CheckboxMultiField
    roi_image_path: Path
    selected_options: list[str]
    user_corrections: list[str] | None = None

    def get_text(self) -> str:
        if self.user_corrections is not None:
            return ','.join(self.user_corrections)
        else:
            return ','.join(self.selected_options)

    def handle_no_correction(self) -> None:
        # If not checkboxes are checked the form element is missing
        self.user_corrections = []

    def set_correction(self, correction: list[str]) -> None:
        if self.selected_options != correction:
            self.user_corrections = correction

    def get_html_input(self) -> str:
        valid_options = self.selected_options
        if self.user_corrections is not None:
            valid_options = self.user_corrections

        checkboxes = []
        for option in self.field.options:
            checkboxes.append(f'<label>{option.name}</label>')
            checkboxes.append(f'''
                <input
                    type="checkbox"
                    name="{self.field_name}"
                    value="{option.name}"
                     {"checked" if option.name in valid_options else ""}
                />
            ''')

        return '\n'.join(checkboxes)


FieldResult = OcrResult | CheckboxResult
