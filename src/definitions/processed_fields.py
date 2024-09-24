from dataclasses import dataclass
from pathlib import Path

import src.validation.util as validation_util

from . import base_fields as fields
from . import util


@dataclass
class BaseProcessedField:
    name: str
    page_region: str
    roi_image_path: Path
    validation_result: validation_util.ValidationResult

    def get_form_name(self) -> str:
        return f'{self.page_region}-{self.name}'

    def get_validation_image_html(self) -> str:
        if self.validation_result.reasoning is None:
            img_tooltip = validation_util.get_base_reasoning(self.validation_result.state)
        else:
            img_tooltip = self.validation_result.reasoning

        return f'''
            <img 
                src="{validation_util.get_result_image_path(self.validation_result.state)}"
                style="width: 20px; height: 20px;"
                title="{img_tooltip}"
            >
        '''


@dataclass
class TextProcessedField(BaseProcessedField):
    base_field: fields.TextField
    text: str
    had_previous_field: bool
    copied_from_previous: bool

    # def get_text(self) -> str:
    #     return self.text
    #
    # def handle_no_correction(self) -> None:
    #     # Text fields always come back on HTML forms
    #     pass
    #
    # def set_correction(self, correction: str) -> None:
    #     self.text = correction

    def get_html_input(self) -> str:
        form_name = self.get_form_name()
        input_disabled_str = 'disabled' if self.had_previous_field and self.copied_from_previous else ''

        html_elements = [
            f'<input type="text" name="{form_name}" class="corrections-box" value="{self.text}" {input_disabled_str}/>'
        ]
        if self.had_previous_field:
            checked_str = 'checked' if self.copied_from_previous else ''
            html_elements.append(f'<input type="checkbox" id="{form_name}-link" class="link-checkbox" {checked_str}>')
            html_elements.append('<label>Link</label>')

        return f'<div style="display: flex;">{"".join(html_elements)}</div>'


@dataclass
class MultiCheckboxProcessedOption:
    name: str
    checked: bool
    text: str | None


@dataclass
class MultiCheckboxProcessedField(BaseProcessedField):
    base_field: fields.MultiCheckboxField
    checkboxes: dict[str, MultiCheckboxProcessedOption]

    # def get_text(self) -> str:
    #     # TODO: How does this need to be exported?
    #     return ''
    #
    # def handle_no_correction(self) -> None:
    #     # If no checkboxes are checked the form element is missing
    #     for option_result in self.option_results.values():
    #         option_result.selected = False
    #         option_result.optional_text = '' if isinstance(option_result.text, str) else None
    #
    # def set_correction(self, correction: list[str]) -> None:
    #     for option_name, result in self.option_results.items():
    #         result.selected = option_name in correction
    #         # TODO: Handle correcting checkboxes with text

    def get_html_input(self) -> str:
        form_name = self.get_form_name()
        table_rows = []

        for checkbox_name, checkbox in self.checkboxes.items():
            table_rows.append('<tr>')
            table_rows.append(f'<td>{util.get_checkbox_html(form_name, checkbox_name, checkbox.checked)}</td>')
            table_rows.append(f'<td><label>{checkbox_name}</label></td>')
            if checkbox.text is not None:
                table_rows.append(f'<td><input type="text" value="{checkbox.text}"/></td>')
            table_rows.append('</td>')

        rows = "\n".join(table_rows)
        return f'<table class="multi-checkbox-table">{rows}</table>'


@dataclass
class CheckboxProcessedField(BaseProcessedField):
    base_field: fields.CheckboxField
    checked: bool

    # def get_text(self) -> str:
    #     return str(self.checked)
    #
    # def handle_no_correction(self) -> None:
    #     self.checked = False
    #
    # def set_correction(self, correction: str) -> None:
    #     self.checked = correction == 'True'

    def get_html_input(self) -> str:
        return util.get_checkbox_html(self.get_form_name(), 'True', self.checked)


@dataclass
class TextOrCheckboxProcessedField(BaseProcessedField):
    base_field: fields.TextOrCheckboxField
    text: str

    # def get_text(self) -> str:
    #     return self.text
    #
    # def handle_no_correction(self) -> None:
    #     # Text fields always come back on HTML forms
    #     pass
    #
    # def set_correction(self, correction: str) -> None:
    #     self.text = correction

    def get_html_input(self) -> str:
        return f'''
            <input type="text" name="{self.get_form_name()}" class="corrections-box" value="{self.text}"/>
        '''


@dataclass
class MultilineTextProcessedField(BaseProcessedField):
    base_field: fields.MultilineTextField
    text: str

    # def get_text(self) -> str:
    #     return self.text
    #
    # def handle_no_correction(self) -> None:
    #     # Text fields always come back on HTML forms
    #     pass
    #
    # def set_correction(self, correction: str) -> None:
    #     self.text = correction

    def get_html_input(self) -> str:
        return f'''
            <input type="text" name="{self.get_form_name()}" class="corrections-box" value="{self.text}"/>
        '''
