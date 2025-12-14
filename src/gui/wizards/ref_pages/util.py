from typing import Any

from PyQt6.QtCore import pyqtProperty
from PyQt6.QtWidgets import QWidget


class DummyField(QWidget):
    def __init__(self) -> None:
        super().__init__(None)
        self.value: Any = ''

    def set_value(self, value: Any) -> None:
        self.value = str(value)

    def get_value(self) -> Any:
        return self.value

    custom_value = pyqtProperty(str, fget=get_value, fset=set_value)
