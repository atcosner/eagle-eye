import logging
import sys
from PyQt6.QtWidgets import QApplication

from src.gui.windows.job_selector import JobSelector
from src.util.logging import configure_root_logger

configure_root_logger(logging.INFO)

app = QApplication(sys.argv)

window = JobSelector()
window.show()

app.exec()
