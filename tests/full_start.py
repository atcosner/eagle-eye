import logging
import sys
from PyQt6.QtWidgets import QApplication

from src.gui.windows.main_window import MainWindow
from src.util.logging import configure_root_logger

configure_root_logger(logging.INFO)

app = QApplication(sys.argv)
app.setQuitOnLastWindowClosed(True)

window = MainWindow()
window.start()

app.exec()
