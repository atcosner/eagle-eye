from dataclasses import dataclass
from pathlib import Path

from src.definitions.fields import TextField, MultiCheckboxField, CheckboxField, TextFieldOrCheckbox, MultilineTextField
from src.definitions.validation import ValidationResult, get_result_image_path


@dataclass
class BaseResult:
    field_name: str
    page_region: str
    roi_image_path: Path

    def get_html_form_name(self) -> str:
        return f'{self.page_region}-{self.field_name}'

    def get_validation_image_html(self) -> str:
        try:
            result = getattr(self, 'validation_result')
        except AttributeError:
            if isinstance(self, TextResult):
                raise RuntimeError('Result member name has changed')
            result = ValidationResult.BYPASS

        return f'''
            <img 
                src="{get_result_image_path(result)}"
                style="width: 20px; height: 20px;"
            >
        '''


@dataclass
class TextResult(BaseResult):
    field: TextField
    validation_result: ValidationResult
    text: str

    def get_text(self) -> str:
        return self.text

    def handle_no_correction(self) -> None:
        # Text fields always come back on HTML forms
        pass

    def set_correction(self, correction: str) -> None:
        self.text = correction

        # Re-validate but don't allow corrections
        result, _ = self.field.validator.validate(self.text, allow_correction=False)
        self.validation_result = result

    def get_html_input(self) -> str:
        html_elements = []
        if self.field.allow_copy:
            source_name = self.get_html_form_name().replace('bottom', 'top')
            html_elements.append(
                f'''<button
                        type="button"
                        onclick="copyFromTopRegion('{source_name}', '{self.get_html_form_name()}')"
                        class="copy-button"
                    >
                        From Above
                    </button>
                '''
            )

        html_elements.append(
            f'<input type="text" name="{self.get_html_form_name()}" class="corrections-box" value="{self.text}"/>'
        )
        return f'<div style="display: flex;">{"".join(html_elements)}</div>'


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
                    name="{self.get_html_form_name()}"
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
                name="{self.get_html_form_name()}"
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
        # Text fields always come back on HTML forms
        pass

    def set_correction(self, correction: str) -> None:
        self.text = correction

    def get_html_input(self) -> str:
        return f'''
            <input type="text" name="{self.get_html_form_name()}" class="corrections-box" value="{self.text}"/>
        '''


@dataclass
class MultilineTextResult(BaseResult):
    field: MultilineTextField
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
            <input type="text" name="{self.get_html_form_name()}" class="corrections-box" value="{self.text}"/>
        '''


FieldResult = TextResult | CheckboxMultiResult | CheckboxResult | TextOrCheckboxResult | MultilineTextResult
