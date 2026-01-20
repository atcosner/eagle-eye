from PyQt6.QtWidgets import QVBoxLayout, QLabel

from ..util.base_page import BasePage


class StartPage(BasePage):
    def __init__(self):
        super().__init__('Eagle Eye | First Start Wizard')

        self.welcome_text = QLabel(
            'Welcome to Eagle Eye!\nThis wizard will help you get you set up to use the Google Vision API.'
        )

        layout = QVBoxLayout()
        layout.addWidget(self.welcome_text)
        self.setLayout(layout)
