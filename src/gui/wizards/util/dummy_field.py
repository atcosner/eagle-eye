from typing import Any

from PyQt6.QtCore import pyqtProperty, pyqtSignal
from PyQt6.QtWidgets import QWidget


class DummyField(QWidget):
    valueChanged = pyqtSignal(str)

    def __init__(self) -> None:
        super().__init__(None)
        self.value: Any = ''

    def set_value(self, value: Any) -> None:
        new_value = value != self.value
        self.value = str(value)
        if new_value:
            self.valueChanged.emit(self.value)

    def get_value(self) -> Any:
        return self.value

    custom_value = pyqtProperty(str, fget=get_value, fset=set_value)
