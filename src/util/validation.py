from enum import Enum

from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QPixmap

from .resources import GENERIC_ICON_PATH

VALIDATION_ICON_SIZE = QSize(30, 30)


class MultiCheckboxValidation(Enum):
    NONE = 1
    REQUIRE_ONE = 2
    MAXIMUM_ONE = 3
    OPTIONAL = 4


class TextValidatorDatatype(Enum):
    # Builtin validation datatypes

    RAW_TEXT = 1
    DATE = 2
    TIME = 3
    INTEGER = 4
    INTEGER_OR_FLOAT = 5
    LIST_CHOICE = 6
    CSV_OF_CHOICE = 7
    GPS_POINT_DD = 8

    # Add custom validation datatypes below
    # DO NOT CHANGE ANY OF THE NUMBERS ABOVE THIS LINE!!

    KU_GPS_WAYPOINT = 9


def validation_result_image(result: bool | None) -> QPixmap:
    match result:
        case True:
            icon_path = GENERIC_ICON_PATH / 'good.png'
        case False:
            icon_path = GENERIC_ICON_PATH / 'bad.png'
        case None:
            icon_path = GENERIC_ICON_PATH / 'bypass.png'
        case _:
            raise RuntimeError(f'Unhandled type: {type(result)}')

    base_pixmap = QPixmap(str(icon_path))
    return base_pixmap.scaled(
        VALIDATION_ICON_SIZE,
        aspectRatioMode=Qt.AspectRatioMode.KeepAspectRatio,
        transformMode=Qt.TransformationMode.SmoothTransformation,
    )
