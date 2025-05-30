import logging
from pathlib import Path

from PyQt6.QtWidgets import QWidget

from .base import BaseWindow
from ..widgets.file_preview import FilePreview

logger = logging.getLogger(__name__)


class FileViewer(BaseWindow):
    def __init__(self, parent: QWidget | None, image_path: Path):
        super().__init__(parent, 'Pre Processing Result')
        self.setMinimumHeight(700)

        self.viewer = FilePreview()
        self.viewer.update_preview(image_path)

        self.setCentralWidget(self.viewer)
