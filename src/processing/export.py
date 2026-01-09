import logging
import pandas as pd
from collections import defaultdict

from src.util.export import ExportMode, CapitalizationType, MultiCbExportType

from ..database.job import Job
from ..database.exporters.circled_exporter import CircledExporter
from ..database.exporters.multi_checkbox_exporter import MultiCheckboxExporter
from ..database.exporters.text_exporter import TextExporter
from ..database.processed_fields.processed_field import ProcessedField
from ..database.processed_fields.processed_checkbox_field import ProcessedCheckboxField
from ..database.processed_fields.processed_circled_field import ProcessedCircledField
from ..database.processed_fields.processed_multi_checkbox_field import ProcessedMultiCheckboxField
from ..database.processed_fields.processed_multi_checkbox_option import ProcessedMultiCheckboxOption
from ..database.processed_fields.processed_text_field import ProcessedTextField

logger = logging.getLogger(__name__)


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
                Full mode will export all forms, regions, and fields regardless of their verification status.
            """
        case _:
            raise RuntimeError(f"Unknown export mode: {mode}")


def default_variable_name(name: str) -> str:
    return name.strip().lower().replace(' ', '_')


def export_bool_to_string(value: bool) -> str:
    return 'yes' if value else 'no'


def handle_capitalization(value: str, mode: CapitalizationType) -> str:
    if mode is CapitalizationType.LOWER:
        return value.lower()
    elif mode is CapitalizationType.UPPER:
        return value.upper()
    elif mode is CapitalizationType.TITLE:
        return value.title()
    else:
        logger.error(f'Unknown capitalization mode: {mode.name}')
        return value


def custom_text_field_export(
        field: ProcessedTextField,
        exporter: TextExporter,
) -> dict[str, str]:
    export_columns = {}
    if exporter.no_export:
        return export_columns

    export_name = default_variable_name(field.name)
    if exporter.export_field_name is not None:
        export_name = exporter.export_field_name

    if field.from_controlled_language is not None:
        # Add a column for the controlled language checkbox
        export_columns[f'{export_name}_checkbox'] = export_bool_to_string(field.from_controlled_language)

    # Work through the custom export options
    export_text = handle_capitalization(field.text, exporter.capitalization)
    if exporter.strip_value:
        export_text = export_text.strip()
    if export_text:
        if exporter.prefix:
            export_text = f'{exporter.prefix}{export_text}'
        if exporter.suffix:
            export_text = f'{export_text}{exporter.suffix}'

    export_columns[export_name] = export_text
    return export_columns


def custom_circled_field_export(
        field: ProcessedCircledField,
        exporter: CircledExporter,
) -> dict[str, str]:
    export_columns = {}
    if exporter.no_export:
        return export_columns

    export_name = default_variable_name(field.name)
    if exporter.export_field_name is not None:
        export_name = exporter.export_field_name

    # Determine the value string
    export_value: str = ''
    for option in field.options.values():
        if option.circled:
            export_value = option.name
            break

    export_columns[export_name] = handle_capitalization(export_value, exporter.capitalization)
    return export_columns


def custom_multi_checkbox_field_export(
        field: ProcessedMultiCheckboxField,
        exporter: MultiCheckboxExporter,
) -> dict[str, str]:
    export_columns = {}
    if exporter.no_export:
        return export_columns

    export_name = default_variable_name(field.name)
    if exporter.export_field_name is not None:
        export_name = exporter.export_field_name

    # Handle single column vs multi column exports
    if exporter.export_type is MultiCbExportType.SINGLE_COLUMN:
        checked_option: ProcessedMultiCheckboxOption | None = None
        for option in field.checkboxes.values():
            if option.checked:
                checked_option = option

        if checked_option is None:
            export_columns[export_name] = ''
        else:
            export_columns[export_name] = checked_option.name

            if checked_option.circled_options:
                for option in checked_option.circled_options.values():
                    if option.circled:
                        export_columns[export_name] = f'{checked_option.name}: {option.name}'

        # TODO: handle options with text fields

    elif exporter.export_type is MultiCbExportType.MULTIPLE_COLUMNS:
        for option in field.checkboxes.values():
            option_name = f'{export_name}_{default_variable_name(option.name)}'
            export_columns[option_name] = export_bool_to_string(option.checked)

            # Add an '_desc' if the checkbox option has a text region
            if option.ocr_text is not None or option.text is not None:
                export_columns[f'{option_name}_desc'] = option.text

    else:
        logger.error(f'Unknown export type: {exporter.export_type.name}')
        return export_columns

    # Update capitalization on all values in our export
    for key, value in export_columns.items():
        export_columns[key] = handle_capitalization(value, exporter.capitalization)

    return export_columns


def export_text_field(
        mode: ExportMode,
        field: ProcessedTextField,
) -> dict[str, str]:
    logger.info(f'Exporting text field: {field.name}')
    # TODO: Check validation status for MODERATE mode

    # Handle if the field has a custom exporter
    if field.text_field.text_exporter is not None:
        return custom_text_field_export(field, field.text_field.text_exporter)
    else:
        return custom_text_field_export(field, TextExporter())


def export_checkbox_field(field: ProcessedCheckboxField) -> dict[str, str]:
    logger.info(f'Exporting checkbox field: {field.name}')

    variable_name = default_variable_name(field.name)
    return {variable_name: export_bool_to_string(field.checked)}


def export_circled_field(field: ProcessedCircledField) -> dict[str, str]:
    logger.info(f'Exporting circled field: {field.name}')

    # TODO: Check validation status for MODERATE mode

    if field.circled_field.exporter is not None:
        return custom_circled_field_export(field, field.circled_field.exporter)
    else:
        # TODO: handle this
        variable_name = default_variable_name(field.name)
        return {variable_name: 'TEST'}


def export_multi_checkbox_field(
        mode: ExportMode,
        field: ProcessedMultiCheckboxField,
) -> dict[str, str]:
    logger.info(f'Exporting multi checkbox field: {field.name}')

    # TODO: Check validation status for MODERATE mode

    if field.multi_checkbox_field.exporter is not None:
        return custom_multi_checkbox_field_export(field, field.multi_checkbox_field.exporter)
    else:
        return custom_multi_checkbox_field_export(field, MultiCheckboxExporter())


def export_field(mode: ExportMode, field: ProcessedField) -> dict[str, str]:
    if field.text_field is not None:
        return export_text_field(mode, field.text_field)
    elif field.checkbox_field is not None:
        return export_checkbox_field(field.checkbox_field)
    elif field.multi_checkbox_field is not None:
        return export_multi_checkbox_field(mode, field.multi_checkbox_field)
    elif field.circled_field is not None:
        return export_circled_field(field.circled_field)
    else:
        logger.error(f'Exported nothing for field: {field.id}')
        return {}


def build_export_df(mode: ExportMode, job: Job) -> pd.DataFrame:
    export_data = defaultdict(list)

    for input_file in job.input_files:
        if input_file.container_file:
            continue

        if input_file.process_result is None:
            logger.error(f'Input file ({input_file.path.name}) has not been processed')
            continue

        logger.info(f'Exporting input file: {input_file.path.name}')
        for region in input_file.process_result.regions.values():
            if mode is ExportMode.STRICT and not region.human_verified:
                logger.warning(f'Skipping unverified region: {region.name} (STRICT export mode)')
                continue

            logger.info(f'Exporting region: {region.name}')
            for group in region.groups:
                logger.info(f'Exporting group: {group.name}')
                for field in group.fields:
                    for export_column, export_value in export_field(mode, field).items():
                        export_data[export_column].append(export_value)

    # log the entire export for debug later
    logger.info('Export data:')
    for key, value in export_data.items():
        logger.info(f'{key}: {value}')

    return pd.DataFrame(export_data)
