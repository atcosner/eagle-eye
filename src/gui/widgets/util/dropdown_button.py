from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import QToolButton, QMenu


class DropdownButton(QToolButton):
    def __init__(self):
        super().__init__()

        self.setPopupMode(QToolButton.ToolButtonPopupMode.MenuButtonPopup)
        self.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonFollowStyle)

        # TODO: Maybe we need this on non-Windows OS's?
        # self.setArrowType(Qt.ArrowType.DownArrow)


class FitImageButton(DropdownButton):
    fitToWindow = pyqtSignal()
    fitToWidth = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setText('Fit to ...')

        self.fit_to_window_action = QAction('Window', self)
        self.fit_to_width_action = QAction('Width', self)

        self.menu = QMenu(self)
        self.menu.addAction(self.fit_to_window_action)
        self.menu.addAction(self.fit_to_width_action)
        self.setMenu(self.menu)

        self.fit_to_window_action.triggered.connect(self.fitToWindow)
        self.fit_to_width_action.triggered.connect(self.fitToWidth)
