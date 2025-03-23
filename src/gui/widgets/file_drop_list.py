from PyQt6.QtCore import QSize, QMimeData, QMimeDatabase, QUrl
from PyQt6.QtGui import QIcon, QDragEnterEvent, QDragMoveEvent, QDropEvent
from PyQt6.QtWidgets import QWidget, QListWidget, QListWidgetItem

from pathlib import Path

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

    def add_item(self, url: QUrl) -> None:
        file_path = Path(url.toLocalFile())
        self.addItem(FileItem(file_path))

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
            for url in event.mimeData().urls():
                self.add_item(url)

            event.acceptProposedAction()
