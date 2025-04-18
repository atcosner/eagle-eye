import cv2
import logging
from sqlalchemy.orm import Session

from PyQt6.QtCore import QObject, pyqtSlot, pyqtSignal, QMutex, QMutexLocker

from src.database import DB_ENGINE
from src.database.input_file import InputFile
from src.database.job import Job
from src.database.pre_process_result import PreProcessResult
from src.database.rotation_attempt import RotationAttempt
from src.util.logging import NamedLoggerAdapter
from src.util.status import FileStatus

logger = logging.getLogger(__name__)


class OcrWorker(QObject):
    updateStatus = pyqtSignal(int, FileStatus)
    ocrComplete = pyqtSignal(int)

    def __init__(self, name: str, job_id: int, input_file_id: int, mutex: QMutex):
        super().__init__()
        self.mutex = mutex
        self._job_id = job_id
        self._input_file_id = input_file_id

        self.log = NamedLoggerAdapter(logger, {'name': f'Thread: {name}'})

    @pyqtSlot()
    def start(self) -> None:
        locker = QMutexLocker(self.mutex)
        self.log.info('Staring thread')

        with Session(DB_ENGINE) as session:
            job = session.get(Job, self._job_id)
            input_file = session.get(InputFile, self._input_file_id)
