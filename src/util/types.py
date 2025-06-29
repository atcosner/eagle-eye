from enum import Enum
from pathlib import Path
from typing import NamedTuple

from PyQt6.QtCore import QRectF, QPointF


class BoxBounds(NamedTuple):
    x: int
    y: int
    width: int
    height: int

    def to_widget(self) -> str:
        return f'Top Left: ({self.x}, {self.y}) | Width: {self.width} | Height: {self.height}'

    def to_db(self) -> str:
        return f'{self.x},{self.y},{self.width},{self.height}'

    @staticmethod
    def from_db(db_value: str | None) -> 'BoxBounds | None':
        if db_value is None:
            return None

        int_values = [int(part) for part in db_value.split(',')]
        return BoxBounds(*int_values)

    def to_qt_rect(self) -> QRectF:
        return QRectF(self.x, self.y, self.width, self.height)

    def qt_top_left(self) -> QPointF:
        return QPointF(self.x, self.y)


class FileDetails(NamedTuple):
    db_id: int
    path: Path


class FormLinkingMethod(Enum):
    NO_LINKING = 1
    PREVIOUS_IDENTIFIER = 2
    PREVIOUS_REGION = 3


def get_link_explanation(method: FormLinkingMethod) -> str:
    match method:
        case FormLinkingMethod.NO_LINKING:
            return """
                <u>No Linking</u><br>
                <br>
                Fields will not be allowed to copy values from fields on other regions/forms.
            """
        case FormLinkingMethod.PREVIOUS_IDENTIFIER:
            return """
                <u>Previous Identifier</u><br>
                <br>
                Fields will be allowed to link to the fields on the previous identifier.<br>
                For example, if the current form has an ID of 100, fields will be allowed to link to the form with ID 99.
            """
        case FormLinkingMethod.PREVIOUS_REGION:
            return """
                <u>Previous Region</u><br>
                <br>
                Fields will only be allowed to link to fields on the previous region.<br>
                For example, fields in the bottom region of a page will only be allowed to link to fields in the top region of the page.
            """
        case _:
            raise RuntimeError(f"Unknown linking mode: {method}")


class FormAlignmentMethod(Enum):
    AUTOMATIC = 1
    ALIGNMENT_MARKS = 2


def get_alignment_explanation(method: FormAlignmentMethod) -> str:
    match method:
        case FormAlignmentMethod.AUTOMATIC:
            return """
                <u>Automatic Alignment</u><br>
                <br>
                Eagle Eye will attempt to automatically align the scanned for to the reference form.<br>
                This method is only recommended on forms that have one region (i.e. one form = one specimen).
            """
        case FormAlignmentMethod.ALIGNMENT_MARKS:
            return """
                <u>Alignment Marks</u><br>
                <br>
                This method will use black squares present in the reference form to align the scanned form.<br>
                Please enter the number of expected alignment marks.
            """
        case _:
            raise RuntimeError(f"Unknown export mode: {method}")
