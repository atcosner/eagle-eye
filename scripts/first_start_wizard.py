import logging
import sys

from PyQt6.QtWidgets import QApplication

from src.gui.wizards.first_start_wizard import FirstStartWizard
from src.util.logging import configure_root_logger

logger = logging.getLogger(__name__)

configure_root_logger(logging.INFO)

app = QApplication(sys.argv)
app.setQuitOnLastWindowClosed(True)

wizard = FirstStartWizard()
wizard.exec()
