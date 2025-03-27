from PyQt6.QtCore import QSize, QMimeData, QMimeDatabase, QUrl
from PyQt6.QtGui import QIcon, QDragEnterEvent, QDragMoveEvent, QDropEvent
from PyQt6.QtWidgets import QWidget, QListWidget, QListWidgetItem

from pathlib import Path
from typing import Iterable

from .. import RESOURCES_PATH


class FileItem(QListWidgetItem):
    def __init__(self, file_path: Path) -> None:
        super().__init__()

        self.setText(file_path.name)
        if file_path.suffix == '.pdf':
            self.setIcon(QIcon(str(RESOURCES_PATH / 'pdf_icon.png')))
        else:
            self.setIcon(QIcon(str(RESOURCES_PATH / 'image_icon.png')))

        self._path = file_path

    def path(self) -> str:
        return str(self._path)


class FileDropList(QListWidget):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setIconSize(QSize(40, 40))

        self.setStyleSheet(f'background-position: center; background-image: url({RESOURCES_PATH / "drag_files.png"})')

        self.mime_db = QMimeDatabase()

    def check_drag_event(self, data: QMimeData) -> bool:
        if not data.hasUrls():
            return False

        invalid_file = False
        for url in data.urls():
            mime_type = self.mime_db.mimeTypeForUrl(url)

            if not mime_type.name().startswith('image') and mime_type.name() != 'application/pdf':
                invalid_file = True

        return not invalid_file

    def add_item(self, file_path: QUrl | Path | str) -> None:
        if isinstance(file_path, QUrl):
            file_path = Path(file_path.toLocalFile())
        elif isinstance(file_path, str):
            file_path = Path(file_path)

        self.addItem(FileItem(file_path))

    def add_items(self, files: Iterable[QUrl | Path | str]) -> None:
        prev_item_count = self.count()
        for file in files:
            self.add_item(file)

        # Auto-select the first element if we had no children to start
        if prev_item_count == 0:
            self.setCurrentRow(0)

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
