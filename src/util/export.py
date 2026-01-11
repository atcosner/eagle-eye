from enum import Enum


class ExportMode(Enum):
    STRICT = object()
    MODERATE = object()
    FULL = object()


class MultiCbExportType(Enum):
    MULTIPLE_COLUMNS = object()
    SINGLE_COLUMN = object()


class CapitalizationType(Enum):
    NONE = object()
    UPPER = object()
    LOWER = object()
    TITLE = object()


class ExportType(Enum):
    RAW = object()
    DATE_YMD = object()
    DATE_DMY = object()
    CSV_SEP_COLUMNS = object()
