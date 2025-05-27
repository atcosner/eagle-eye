import logging
import shutil
import uuid
from pathlib import Path
from sqlalchemy.orm import Session
from typing import Iterable

from PyQt6.QtCore import QSize, QMimeData, QMimeDatabase, QUrl
from PyQt6.QtGui import QIcon, QDragEnterEvent, QDragMoveEvent, QDropEvent
from PyQt6.QtPdf import QPdfDocument
from PyQt6.QtWidgets import QWidget, QListWidget, QListWidgetItem

from src.database import DB_ENGINE
from src.database.input_file import InputFile
from src.database.job import Job
from src.util.paths import LocalPaths, is_pdf
from src.util.resources import FILE_TYPE_ICON_PATH
from src.util.types import FileDetails

logger = logging.getLogger(__name__)


class FileItem(QListWidgetItem):
    def __init__(self, db_id: int, file_path: Path) -> None:
        super().__init__()
        self._db_id = db_id
        self._path = file_path

        self.setText(file_path.name)
        icon_file_name = 'pdf_icon.png' if is_pdf(file_path) else 'image_icon.png'
        self.setIcon(QIcon(str(FILE_TYPE_ICON_PATH / icon_file_name)))

    def path(self) -> Path:
        return self._path

    def file_details(self) -> FileDetails:
        return FileDetails(
            db_id=self._db_id,
            path=self._path,
        )


class FileDropList(QListWidget):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setIconSize(QSize(40, 40))

        self._job_db_id: int | None = None
        self._job_db_uuid: uuid.UUID | None = None

        self.mime_db = QMimeDatabase()

    def load_job(self, job: Job | None) -> None:
        self._job_db_id = job.id if job else None
        self._job_db_uuid = job.uuid if job else None

        # Load in the input files if we are loading a job
        self.clear()
        if job is not None:
            for input_file in job.input_files:
                # ignore files that are linked to another file
                if input_file.linked_input_file_id is None:
                    self.add_item(input_file.path, db_id=input_file.id)

    def check_drag_event(self, data: QMimeData) -> bool:
        if not data.hasUrls():
            return False

        invalid_file = False
        for url in data.urls():
            mime_type = self.mime_db.mimeTypeForUrl(url)

            if not mime_type.name().startswith('image') and mime_type.name() != 'application/pdf':
                invalid_file = True

        return not invalid_file

    def add_item(self, file_path: QUrl | Path | str, db_id: int | None = None) -> None:
        if isinstance(file_path, QUrl):
            file_path = Path(file_path.toLocalFile())
        elif isinstance(file_path, str):
            file_path = Path(file_path)

        if db_id is None:
            # Add it to the job in the DB
            with Session(DB_ENGINE) as session:
                job = session.get(Job, self._job_db_id)

                input_file = InputFile(path=file_path)
                job.input_files.append(input_file)

                # commit so that we get a primary key assigned
                session.commit()
                db_id = input_file.id

                # Copy the file into our internal storage
                input_file_directory = LocalPaths.input_file_directory(self._job_db_uuid, db_id)
                input_file_directory.mkdir()
                input_file.path = input_file_directory / file_path.name

                logger.info(f'Copying: "{file_path}" -> "{input_file.path}"')
                shutil.copy(file_path, input_file.path)
                file_path = input_file.path

                # if this is a PDF, create an input file per-page
                if is_pdf(input_file.path):
                    input_file.container_file = True

                    document = QPdfDocument(None)
                    document.load(str(file_path))

                    for idx in range(document.pageCount()):
                        page_path = input_file.path.with_name(f'{input_file.path.stem}_page{idx+1}.png')

                        page_file = InputFile(path=page_path)
                        page_file.linked_input_file_id = input_file.id
                        job.input_files.append(page_file)
                        session.commit()

                        page_file_directory = LocalPaths.input_file_directory(self._job_db_uuid, page_file.id)
                        page_file_directory.mkdir()
                        page_file.path = page_file_directory / page_path.name

                session.commit()

        logger.info(f'Adding file: {file_path}')
        self.addItem(FileItem(db_id, file_path))

    def add_items(self, files: Iterable[QUrl | Path | str]) -> None:
        prev_item_count = self.count()
        for file in files:
            self.add_item(file)

        # Auto-select the first element if we had no children to start
        if prev_item_count == 0:
            self.setCurrentRow(0)

    def get_files(self) -> list[FileDetails]:
        return [self.item(idx).file_details() for idx in range(self.count())]

    #
    # Drag and Drop behavior
    #
    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        if self.check_drag_event(event.mimeData()):
            event.acceptProposedAction()
        else:
            event.ignore()

    def dragMoveEvent(self, event: QDragMoveEvent) -> None:
        if self.check_drag_event(event.mimeData()):
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event: QDropEvent) -> None:
        if event.mimeData().hasUrls():
            self.add_items(event.mimeData().urls())

            event.acceptProposedAction()
