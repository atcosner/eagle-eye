from PyQt6.QtWidgets import QWizard, QWidget

from .first_start_pages.api_setup_page import ApiSetupPage
from .first_start_pages.start_page import StartPage


class FirstStartWizard(QWizard):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setWindowTitle('Eagle Eye | Set Up Wizard')
        self.setWizardStyle(QWizard.WizardStyle.ModernStyle)

        self.addPage(StartPage())
        self.addPage(ApiSetupPage())
        # self.addPage(AlignmentPage())
