import logging
import sys
from PyQt6.QtWidgets import QApplication, QMainWindow

from src.gui.dialogs.reference_form_builder import ReferenceFormBuilder
from src.util.logging import configure_root_logger

configure_root_logger(logging.INFO)

app = QApplication(sys.argv)
app.setQuitOnLastWindowClosed(True)

form_builder = ReferenceFormBuilder(None, True, 1)
form_builder.exec()
