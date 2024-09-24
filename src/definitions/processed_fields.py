import logging
from dataclasses import dataclass
from pathlib import Path

import src.validation.util as validation_util

from . import base_fields as fields
from . import util

logger = logging.getLogger(__name__)

FormUpdateDict = dict[str, str | list[str]]


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

    def handle_form_update(self, form_dict: FormUpdateDict) -> None:
        raise NotImplementedError('BaseProcessedField.handle_form_update() must be overridden')

    def handle_no_form_update(self) -> None:
        pass


@dataclass
class TextProcessedField(BaseProcessedField):
    base_field: fields.TextField
    text: str
    had_previous_field: bool
    copied_from_previous: bool

    # def get_text(self) -> str:
    #     return self.text

    def handle_form_update(self, form_dict: FormUpdateDict) -> None:
        logger.info(form_dict)
        self.text = form_dict[self.get_form_name()]

    def get_html_input(self) -> str:
        form_name = self.get_form_name()
        input_editable_str = 'readonly' if self.had_previous_field and self.copied_from_previous else ''

        html_elements = [
            f'<input type="text" name="{form_name}" class="corrections-box" value="{self.text}" {input_editable_str}/>'
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

    def handle_no_form_update(self) -> None:
        # If no checkboxes are checked the form element is missing
        for checkbox in self.checkboxes.values():
            checkbox.checked = False
            checkbox.text = '' if checkbox.text is not None else None

    def handle_form_update(self, form_dict: FormUpdateDict) -> None:
        logger.info(form_dict)
        selected_options = form_dict[self.get_form_name()]
        for checkbox_name, checkbox in self.checkboxes.items():
            checkbox.selected = checkbox_name in selected_options
            if checkbox.selected and checkbox.text is not None:
                # Attempt to grab the text from the form
                checkbox.text = form_dict[f'{self.get_form_name()}-{checkbox_name}-text']

    def get_html_input(self) -> str:
        form_name = self.get_form_name()
        table_rows = []

        for checkbox_name, checkbox in self.checkboxes.items():
            table_rows.append('<tr>')
            table_rows.append(f'<td>{util.get_checkbox_html(form_name, checkbox_name, checkbox.checked)}</td>')
            table_rows.append(f'<td><label>{checkbox_name}</label></td>')
            if checkbox.text is not None:
                disabled_str = 'disabled' if not checkbox.checked else ''
                table_rows.append(
                    f'<td><input type="text" name="{form_name}-{checkbox_name}-text" value="{checkbox.text}" {disabled_str}/></td>'
                )
            table_rows.append('</td>')

        rows = "\n".join(table_rows)
        return f'<table class="multi-checkbox-table">{rows}</table>'


@dataclass
class CheckboxProcessedField(BaseProcessedField):
    base_field: fields.CheckboxField
    checked: bool

    # def get_text(self) -> str:
    #     return str(self.checked)

    def handle_no_form_update(self) -> None:
        self.checked = False

    def handle_form_update(self, form_dict: FormUpdateDict) -> None:
        logger.info(form_dict)
        self.checked = (form_dict[self.get_form_name()] == 'True')

    def get_html_input(self) -> str:
        return util.get_checkbox_html(self.get_form_name(), 'True', self.checked)


@dataclass
class TextOrCheckboxProcessedField(BaseProcessedField):
    base_field: fields.TextOrCheckboxField
    text: str

    # def get_text(self) -> str:
    #     return self.text

    def handle_form_update(self, form_dict: FormUpdateDict) -> None:
        logger.info(form_dict)
        self.text = form_dict[self.get_form_name()]

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

    def handle_form_update(self, form_dict: FormUpdateDict) -> None:
        logger.info(form_dict)
        self.text = form_dict[self.get_form_name()]

    def get_html_input(self) -> str:
        return f'''
            <input type="text" name="{self.get_form_name()}" class="corrections-box" value="{self.text}"/>
        '''
