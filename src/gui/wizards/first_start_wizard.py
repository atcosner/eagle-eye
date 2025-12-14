from PyQt6.QtWidgets import QWizard, QWidget

# from .first_start_pages



class FirstStartWizard(QWizard):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setWindowTitle('Eagle Eye | New Install Wizard')
        self.setWizardStyle(QWizard.WizardStyle.ModernStyle)

        # self.addPage(StartPage())
        # self.addPage(RegionsPage())
        # self.addPage(AlignmentPage())
        # self.addPage(LinkingPage())
        # self.addPage(FilePage())
