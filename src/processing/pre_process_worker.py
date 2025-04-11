import logging
from pathlib import Path

from PyQt6.QtCore import QObject, pyqtSlot, pyqtSignal

from ..util.status import FileStatus

logger = logging.getLogger()


class PreProcessingWorker(QObject):
    updateStatus = pyqtSignal(FileStatus)

    def __init__(self, input_file: Path):
        super().__init__()
        self.input_file = input_file

    @pyqtSlot()
    def start(self) -> None:
        logger.info('Staring thread')
