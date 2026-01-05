from PyQt6.QtWidgets import QWizard, QWidget

from .first_start_pages.project_page import ProjectPage
from .first_start_pages.start_page import StartPage


class FirstStartWizard(QWizard):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setWindowTitle('Eagle Eye | First Start Wizard')
        self.setWizardStyle(QWizard.WizardStyle.ModernStyle)

        self.addPage(StartPage())
        self.addPage(ProjectPage())
