import logging
import sys
from PyQt6.QtWidgets import QApplication

from src.gui.windows.result_viewer import ResultViewer
from src.util.logging import configure_root_logger

configure_root_logger(logging.INFO)

app = QApplication(sys.argv)
app.setQuitOnLastWindowClosed(True)

window = ResultViewer()
window.load_job(10)
window.show()

app.exec()
