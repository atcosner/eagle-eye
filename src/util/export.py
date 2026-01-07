from enum import Enum


class ExportMode(Enum):
    STRICT = object()
    MODERATE = object()
    FULL = object()


class MultiCbExportType(Enum):
    MULTIPLE_COLUMNS = object()
    SINGLE_COLUMN = object()
