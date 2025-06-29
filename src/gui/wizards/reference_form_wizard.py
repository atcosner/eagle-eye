from PyQt6.QtWidgets import QWizard, QWidget

from .pages.alignment_page import AlignmentPage
from .pages.file_page import FilePage
from .pages.linking_page import LinkingPage
from .pages.regions_page import RegionsPage
from .pages.start_page import StartPage


class ReferenceFormWizard(QWizard):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setWindowTitle('Eagle Eye | Reference Form Wizard')
        self.setWizardStyle(QWizard.WizardStyle.ModernStyle)

        self.addPage(StartPage())
        self.addPage(RegionsPage())
        self.addPage(AlignmentPage())
        self.addPage(LinkingPage())
        self.addPage(FilePage())
