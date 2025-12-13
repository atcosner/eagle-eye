import itertools
import logging
from enum import Enum
from rapidfuzz import process, fuzz, utils
from typing import Iterable

from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QPixmap, QIcon

from .resources import GENERIC_ICON_PATH

VALIDATION_ICON_SIZE = QSize(30, 30)
VALID_TIME_FORMATS = ('h:mm', 'hh:mm')
VALID_DATE_FORMATS = [
    # formats produced by the qt widgets
    'MM/dd/yyyy',
    'M/d/yyyy',
] + [
    # formats we could see from user input
    ' '.join(x) for x in itertools.product(
        *[
            ('d', 'dd'),
            ('MMM', 'MMMM'),
            ('yy', 'yyyy')
        ]
    )
]

logger = logging.getLogger(__name__)


class MultiChoiceValidation(Enum):
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
    FN_COUNTRY_STATE = 10


def get_verified_icon(verified: bool) -> QIcon:
    icon = 'good.png' if verified else 'bad.png'
    return QIcon(str(GENERIC_ICON_PATH / icon))


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


def find_best_string_match(text: str, options: Iterable[str]) -> str | None:
    match, ratio, edits = process.extractOne(
        text,
        options,
        scorer=fuzz.WRatio,
        processor=utils.default_process,
    )
    logger.info(f'Best match: "{text}" -> "{match}", ratio: {ratio}, edits: {edits}')
    return match if ratio > 65 else None
