import logging
import sys
from PyQt6.QtWidgets import QApplication

from src.gui.windows.vision_api_config import VisionApiConfig
from src.util.logging import configure_root_logger

configure_root_logger(logging.INFO)

app = QApplication(sys.argv)
app.setQuitOnLastWindowClosed(True)

window = VisionApiConfig()
window.show()

app.exec()
