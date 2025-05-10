import logging
import sys
from PyQt6.QtWidgets import QApplication, QMainWindow

from src.gui.widgets.reference_form_creation import ReferenceFormCreation
from src.util.logging import configure_root_logger

configure_root_logger(logging.INFO)

app = QApplication(sys.argv)
app.setQuitOnLastWindowClosed(True)

form_creator = ReferenceFormCreation()

window = QMainWindow()
window.setCentralWidget(form_creator)
window.resize(600, 900)
window.show()

form_creator.load_reference_form(1)

app.exec()
