from PyQt6.QtWidgets import QWizard, QWidget

from .pages.start_page import StartPage


class ReferenceFormWizard(QWizard):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setWindowTitle('Eagle Eye | Reference Form Wizard')
        self.setWizardStyle(QWizard.WizardStyle.ModernStyle)

        self.addPage(StartPage())
