import pandas as pd
from enum import Enum

from ..database.job import Job


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


def build_export_df(job: Job) -> pd.DataFrame:
    pass
