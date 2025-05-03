import logging
from collections import defaultdict

import pandas as pd
from enum import Enum

from ..database.job import Job
from ..database.processed_fields.processed_field import ProcessedField
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


def export_text_field(field: ProcessedTextField) -> dict[str, str]:
    pass


def export_field(mode: ExportMode, field: ProcessedField) -> dict[str, str]:
    # TODO: Check validation status for MODERATE mode
    if field.text_field is not None:
        return export_text_field(field.text_field)
    else:
        logger.error(f'Exported nothing for field: {field.id}')
        return {}


def build_export_df(mode: ExportMode, job: Job) -> pd.DataFrame:
    export_data = defaultdict(list)

    for input_file in job.input_files:
        if input_file.process_result is None:
            logger.error(f'Input file ({input_file.name}) has not been processed')
            continue

        logger.info(f'Exporting input file: {input_file.name}')
        for region in input_file.regions.values():
            if mode is ExportMode.STRICT and not region.verified:
                logger.warning(f'Skipping region: {region.name} (STRICT export mode)')
                continue

            logger.info(f'Exporting region: {region.name}')
            for field in region.fields:
                logger.info(f'Exporting field: {field.name}')

                for export_column, export_value in export_field(mode, field):
                    export_data[export_column].append(export_value)

    return pd.DataFrame(export_data)
