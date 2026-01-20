import logging
import sys

from PyQt6.QtWidgets import QApplication

from src.gui.windows.reference_form_editor import ReferenceFormEditor
from src.util.logging import configure_root_logger

configure_root_logger(logging.INFO)

app = QApplication(sys.argv)
app.setQuitOnLastWindowClosed(True)

form_editor = ReferenceFormEditor(None, True, 2)
form_editor.show()

app.exec()
