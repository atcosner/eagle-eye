import logging

from PyQt6.QtWidgets import QWidget

logger = logging.getLogger(__name__)


class ResultExport(QWidget):
    def __init__(self):
        super().__init__()
