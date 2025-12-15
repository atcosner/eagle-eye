from PyQt6.QtWidgets import QVBoxLayout, QLabel

from .first_start_page import FirstStartPage


class ApiSetupPage(FirstStartPage):
    def __init__(self):
        super().__init__()
        self.setSubTitle('Google API Setup')

        self._set_up_layout()

    def _set_up_layout(self) -> None:
        layout = QVBoxLayout()
        layout.addWidget(QLabel('Welcome to the Eagle Eye Setup Wizard!'))
        layout.addSpacing(10)
        layout.addWidget(QLabel('This wizard will help you get your Google API configuration set up and load some example Reference Forms'))
        self.setLayout(layout)
