from dataclasses import dataclass
from pathlib import Path

from src.definitions.fields import TextField, MultiCheckboxField, CheckboxField, TextFieldOrCheckbox


@dataclass
class BaseResult:
    field_name: str
    page_region: str
    roi_image_path: Path


@dataclass
class TextResult(BaseResult):
    field: TextField
    text: str

    def get_text(self) -> str:
        return self.text

    def handle_no_correction(self) -> None:
        # Text fields always come back on HTML forms
        pass

    def set_correction(self, correction: str) -> None:
        self.text = correction

    def get_html_input(self) -> str:
        return f'''
            <input type="text" name="{self.field_name}" class="corrections-box" value="{self.text}"/>
        '''


@dataclass
class CheckboxMultiResult(BaseResult):
    field: MultiCheckboxField
    selected_options: list[str]

    def get_text(self) -> str:
        return ','.join(self.selected_options)

    def handle_no_correction(self) -> None:
        # If no checkboxes are checked the form element is missing
        self.selected_options = []

    def set_correction(self, correction: list[str]) -> None:
        self.selected_options = correction

    def get_html_input(self) -> str:
        checkboxes = []
        for option in self.field.options:
            checkboxes.append(f'''
                <input
                    type="checkbox"
                    name="{self.field_name}"
                    value="{option.name}"
                     {"checked" if option.name in self.selected_options else ""}
                />
            ''')
            checkboxes.append(f'<label>{option.name},</label>')

        return '\n'.join(checkboxes)


@dataclass
class CheckboxResult(BaseResult):
    field: CheckboxField
    checked: bool

    def get_text(self) -> str:
        return str(self.checked)

    def handle_no_correction(self) -> None:
        self.checked = False

    def set_correction(self, correction: str) -> None:
        self.checked = correction == 'True'

    def get_html_input(self) -> str:
        return f'''
            <input
                type="checkbox"
                name="{self.field_name}"
                class="corrections-box"
                value="True"
                {"checked" if self.checked else ""}
            />
        '''


@dataclass
class TextOrCheckboxResult(BaseResult):
    field: TextFieldOrCheckbox
    text: str

    def get_text(self) -> str:
        return self.text

    def handle_no_correction(self) -> None:
        # TODO
        pass

    def set_correction(self, correction: str) -> None:
        # TODO
        pass

    def get_html_input(self) -> str:
        return f'''
            <input type="text" name="{self.field_name}" class="corrections-box" value="{self.text}"/>
        '''


FieldResult = TextResult | CheckboxMultiResult | CheckboxResult | TextOrCheckboxResult
