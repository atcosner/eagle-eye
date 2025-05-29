import logging
import sys

from PyQt6.QtWidgets import QApplication

from src.gui.wizards.reference_form_wizard import ReferenceFormWizard
from src.util.logging import configure_root_logger

configure_root_logger(logging.INFO)

app = QApplication(sys.argv)
app.setQuitOnLastWindowClosed(True)

form_wizard = ReferenceFormWizard()
form_wizard.exec()
