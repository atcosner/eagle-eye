import logging
from sqlalchemy.orm import Session

from PyQt6.QtWidgets import QWidget, QTabWidget

from src.database import DB_ENGINE
from src.database.input_file import InputFile
from src.util.logging import NamedLoggerAdapter

from .base import BaseWindow
from ..widgets.file_preview import FilePreview

logger = logging.getLogger(__name__)


class PreProcessingResult(BaseWindow):
    def __init__(self, parent: QWidget | None, db_id: int):
        super().__init__(parent, 'Pre Processing Result')
        self.setMinimumHeight(700)

        self.log = NamedLoggerAdapter(logger, name=db_id)

        self.main_tabs = QTabWidget()
        self.rotation_tabs = QTabWidget()

        self.rotation_viewers: dict[int, FilePreview] = {}
        self.matches_viewer = FilePreview()
        self.aligned_viewer = FilePreview()
        self.overlaid_viewer = FilePreview()

        self._set_up_layout()
        self._load_input_file(db_id)

    def _set_up_layout(self) -> None:
        self.setCentralWidget(self.main_tabs)

        self.main_tabs.addTab(self.rotation_tabs, 'Rotations')
        self.main_tabs.addTab(self.matches_viewer, 'Matched Points')
        self.main_tabs.addTab(self.aligned_viewer, 'Aligned Image')
        self.main_tabs.addTab(self.overlaid_viewer, 'Overlaid Image')

    def _load_input_file(self, db_id: int) -> None:
        self.rotation_tabs.clear()

        with Session(DB_ENGINE) as session:
            input_file = session.get(InputFile, db_id)
            if input_file is None:
                self.log.error(f'ID {db_id} was not found in the DB')
                return

            self.update_title(f'Pre Processing Result | {input_file.path.name}')
            result = input_file.pre_process_result

            # Send the images to our previews
            self.matches_viewer.update_preview(result.matches_image_path)
            self.aligned_viewer.update_preview(result.aligned_image_path)
            self.overlaid_viewer.update_preview(result.overlaid_image_path)

            # Create a tab for each rotation attempt
            for angle, attempt in sorted(result.rotation_attempts.items(), key=lambda x: x[0]):
                preview = FilePreview()
                preview.update_preview(attempt.path)

                index = self.rotation_tabs.addTab(preview, str(angle))
                self.rotation_viewers[angle] = preview

                # Focus on the accepted rotation
                if angle == result.accepted_rotation_angle:
                    self.rotation_tabs.setTabText(index, f'* {angle} *')
                    self.rotation_tabs.setCurrentIndex(index)
