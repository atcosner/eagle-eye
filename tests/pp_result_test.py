import logging
import sys
from PyQt6.QtWidgets import QApplication

from src.gui.windows.pre_processing_result import PreProcessingResult
from src.util.logging import configure_root_logger

configure_root_logger(logging.INFO)

app = QApplication(sys.argv)
app.setQuitOnLastWindowClosed(True)

window = PreProcessingResult(19)
window.show()

app.exec()
