import logging
from collections import defaultdict

import pandas as pd
from enum import Enum

from ..database.job import Job
from ..database.exporters.text_exporter import TextExporter
from ..database.processed_fields.processed_field import ProcessedField
from ..database.processed_fields.processed_checkbox_field import ProcessedCheckboxField
from ..database.processed_fields.processed_multi_checkbox_field import ProcessedMultiCheckboxField
from ..database.processed_fields.processed_multiline_text_field import ProcessedMultilineTextField
from ..database.processed_fields.processed_text_field import ProcessedTextField

logger = logging.getLogger(__name__)


class ExportMode(Enum):
    STRICT = object()
    MODERATE = object()
    FULL = object()


def get_mode_explanation(mode: ExportMode) -> str:
    match mode:
        case ExportMode.STRICT:
            return """
                <u>Strict Mode</u><br>
                <br>
                Strict mode will only export forms/regions that have been fully verified in Step 4.<br>
            """
        case ExportMode.MODERATE:
            return """
                <u>Moderate Mode</u><br>
                <br>
                Moderate mode will export all forms, and regions irregardless of their verification status, but<br>
                will not export data for fields that have failed their verification.
            """
        case ExportMode.FULL:
            return """
                <u>Full Mode</u><br>
                <br>
                Full mode will export all forms, regions, and fields irregardless of their verification status.
            """
        case _:
            raise RuntimeError(f"Unknown export mode: {mode}")


def default_variable_name(name: str) -> str:
    return name.strip().lower().replace(' ', '_')


def export_bool_to_string(value: bool) -> str:
    return 'yes' if value else 'no'


def custom_text_field_export(
        field: ProcessedTextField | ProcessedMultilineTextField,
        exporter: TextExporter,
) -> dict[str, str]:
    export_columns = {}
    if exporter.no_export:
        return export_columns

    base_variable_name = default_variable_name(field.name)
    if exporter.export_field_name is not None:
        base_variable_name = exporter.export_field_name

    if field.from_controlled_language is not None:
        # Add a column for the controlled language checkbox
        export_columns[f'{base_variable_name}_checkbox'] = export_bool_to_string(field.from_controlled_language)

    # Work through the custom export options
    export_text = field.text
    if exporter.strip_value:
        export_text = export_text.strip()
    if exporter.prefix:
        export_text = f'{exporter.prefix}{export_text}'
    if exporter.suffix:
        export_text = f'{export_text}{exporter.suffix}'

    export_columns[base_variable_name] = export_text
    return export_columns


def export_text_field(
        mode: ExportMode,
        field: ProcessedTextField | ProcessedMultilineTextField,
) -> dict[str, str]:
    logger.info(f'Exporting text field: {field.name}')
    is_test_field = isinstance(field, ProcessedTextField)

    # TODO: Check validation status for MODERATE mode

    # Handle if the field has a custom exporter
    exporter = field.text_field.text_exporter if is_test_field else field.multiline_text_field.text_exporter
    if exporter is not None:
        return custom_text_field_export(field, exporter)
    else:
        export_columns = {}
        base_variable_name = default_variable_name(field.name)

        # Handle controlled language without a custom exporter
        if field.from_controlled_language is not None:
            # Add a column for the controlled language checkbox
            export_columns[f'{base_variable_name}_checkbox'] = export_bool_to_string(field.from_controlled_language)

        export_columns[base_variable_name] = field.text.lower()
        return export_columns


def export_checkbox_field(field: ProcessedCheckboxField) -> dict[str, str]:
    logger.info(f'Exporting checkbox field: {field.name}')

    variable_name = default_variable_name(field.name)
    return {variable_name: export_bool_to_string(field.checked)}


def export_multi_checkbox_field(
        mode: ExportMode,
        field: ProcessedMultiCheckboxField,
) -> dict[str, str]:
    logger.info(f'Exporting multi checkbox field: {field.name}')
    base_variable_name = default_variable_name(field.name)

    # TODO: Check validation status for MODERATE mode

    export_columns = {}
    for checkbox_option in field.checkboxes.values():
        option_variable_name = f'{base_variable_name}_{default_variable_name(checkbox_option.name)}'
        export_columns[option_variable_name] = export_bool_to_string(checkbox_option.checked)

        # Add an '_desc' if the checkbox option has a text region
        if checkbox_option.ocr_text is not None or checkbox_option.text is not None:
            export_columns[f'{option_variable_name}_desc'] = checkbox_option.text

    return export_columns


def export_field(mode: ExportMode, field: ProcessedField) -> dict[str, str]:
    if field.text_field is not None:
        return export_text_field(mode, field.text_field)
    elif field.multiline_text_field is not None:
        return export_text_field(mode, field.multiline_text_field)
    elif field.checkbox_field is not None:
        return export_checkbox_field(field.checkbox_field)
    elif field.multi_checkbox_field is not None:
        return export_multi_checkbox_field(mode, field.multi_checkbox_field)
    else:
        logger.error(f'Exported nothing for field: {field.id}')
        return {}


def build_export_df(mode: ExportMode, job: Job) -> pd.DataFrame:
    export_data = defaultdict(list)

    for input_file in job.input_files:
        if input_file.process_result is None:
            logger.error(f'Input file ({input_file.path.name}) has not been processed')
            continue

        logger.info(f'Exporting input file: {input_file.path.name}')
        for region in input_file.process_result.regions.values():
            if mode is ExportMode.STRICT and not region.human_verified:
                logger.warning(f'Skipping unverified region: {region.name} (STRICT export mode)')
                continue

            logger.info(f'Exporting region: {region.name}')
            for field in region.fields:
                for export_column, export_value in export_field(mode, field).items():
                    export_data[export_column].append(export_value)

    # for column, values in export_data.items():
    #     print(f'{column}: {len(values)} : {values}')

    return pd.DataFrame(export_data)
