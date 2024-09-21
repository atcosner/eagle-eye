from dataclasses import dataclass
from pathlib import Path

from . import fields as fields
from . import util as util


@dataclass
class BaseResult:
    page_region: str
    field: fields.FormField
    roi_image_path: Path

    def validate(self) -> util.ValidationResult:
        return self.field.validator.validate(self, allow_correction=True)

    def get_html_form_name(self) -> str:
        return f'{self.page_region}-{self.field.name}'

    def get_validation_image_html(self) -> str:
        return f'''
            <img 
                src="{util.get_result_image_path(self.validate())}"
                style="width: 20px; height: 20px;"
            >
        '''


@dataclass
class TextResult(BaseResult):
    text: str

    def get_text(self) -> str:
        return self.text

    def handle_no_correction(self) -> None:
        # Text fields always come back on HTML forms
        pass

    def set_correction(self, correction: str) -> None:
        self.text = correction

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
class CheckboxOptionResult:
    checked: bool
    text: str | None


@dataclass
class CheckboxMultiResult(BaseResult):
    option_results: dict[str, CheckboxOptionResult]

    def get_text(self) -> str:
        # TODO: How does this need to be exported?
        return ''

    def handle_no_correction(self) -> None:
        # If no checkboxes are checked the form element is missing
        for option_result in self.option_results.values():
            option_result.selected = False
            option_result.optional_text = '' if isinstance(option_result.text, str) else None

    def set_correction(self, correction: list[str]) -> None:
        for option_name, result in self.option_results.items():
            result.selected = option_name in correction
            # TODO: Handle correcting checkboxes with text

    def get_html_input(self) -> str:
        form_name = self.get_html_form_name()
        table_rows = []

        for option_name, result in self.option_results.items():
            table_rows.append('<tr>')
            table_rows.append(f'<td>{util.get_checkbox_html(form_name, option_name, result.checked)}</td>')
            table_rows.append(f'<td><label>{option_name}</label></td>')
            if result.text is not None:
                table_rows.append(f'<td><input type="text" value="{result.text}"/></td>')
            table_rows.append('</td>')

        rows = "\n".join(table_rows)
        return f'<table>{rows}</table>'


@dataclass
class CheckboxResult(BaseResult):
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
