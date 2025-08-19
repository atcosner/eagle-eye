import logging
from sqlalchemy.orm import Session

from PyQt6.QtCore import pyqtSlot, pyqtSignal
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QHBoxLayout

from src.database import DB_ENGINE
from src.database.input_file import InputFile
from src.gui.widgets.util.sized_scroll_area import SizedScrollArea
from src.gui.widgets.util.vertical_tabs import VerticalTabs
from src.gui.windows.file_viewer import FileViewer
from src.util.validation import get_verified_icon

from .region_ocr_results import RegionOcrResults

logger = logging.getLogger(__name__)


class FileOcrResults(QWidget):
    verificationChange = pyqtSignal(bool, bool)

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self._input_file_db_id: int | None = None
        self._result_db_id: int | None = None
        self._initial_show = False

        self.view_original_button = QPushButton('View Form')
        self.view_original_button.pressed.connect(self.handle_view_original_button)

        self.tabs = VerticalTabs()
        self.tabs.currentChanged.connect(self.handle_current_tab_change)

        self.region_widgets: dict[int, RegionOcrResults] = {}
        self.region_validation: dict[int, bool] = {}

        self._set_up_layout()

    def _set_up_layout(self) -> None:
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.addWidget(self.view_original_button)
        button_layout.addStretch()

        layout = QVBoxLayout()
        layout.addLayout(button_layout)
        layout.addWidget(self.tabs)
        self.setLayout(layout)

    def load_input_file(self, input_file: InputFile | int | None) -> None:
        self.tabs.clear()
        self.region_validation.clear()
        if input_file is None:
            return

        with Session(DB_ENGINE) as session:
            input_file = session.get(InputFile, input_file) if isinstance(input_file, int) else input_file
            if input_file.process_result is None:
                return

            self._input_file_db_id = input_file.id
            self._result_db_id = input_file.process_result.id
            for region in input_file.process_result.regions.values():
                region_results = RegionOcrResults()
                region_results.verificationChange.connect(self.handle_verification_change)
                region_results.load_region(region)

                scroll_area = SizedScrollArea(region_results)
                tab_idx = self.tabs.addTab(scroll_area, region.name)
                self.region_widgets[tab_idx] = region_results
                self.region_validation[tab_idx] = region.human_verified

                # Set the verified icon
                self.tabs.setTabIcon(tab_idx, get_verified_icon(region.human_verified))

    @pyqtSlot(int)
    def handle_current_tab_change(self, new_index: int) -> None:
        if not self._initial_show:
            self._initial_show = True
            return

        region = self.region_widgets[new_index]
        region.handle_tab_shown()

    @pyqtSlot(bool, bool)
    def handle_verification_change(self, new_status: bool, continue_check: bool) -> None:
        current_idx = self.tabs.currentIndex()
        self.region_validation[current_idx] = new_status

        # Update the icon for the tab
        self.tabs.setTabIcon(current_idx, get_verified_icon(new_status))

        move_to_next_file = False
        if continue_check:
            if current_idx >= self.tabs.count() - 1:
                # Move to the next input file
                move_to_next_file = True
            else:
                # Move to the next tab
                self.tabs.setCurrentIndex(current_idx + 1)

        self.verificationChange.emit(all(self.region_validation.values()), move_to_next_file)

    @pyqtSlot()
    def handle_view_original_button(self) -> None:
        with Session(DB_ENGINE) as session:
            input_file = session.get(InputFile, self._input_file_db_id)
            if input_file is None:
                return

            if input_file.pre_process_result is None:
                return

            pre_process = input_file.pre_process_result
            if not pre_process.successful_alignment:
                return

            # automatically aligned images will not have an accepted rotation angle
            if pre_process.accepted_rotation_angle is None:
                original_path = input_file.path
            else:
                original_path = pre_process.rotation_attempts[pre_process.accepted_rotation_angle].path

            viewer = FileViewer(self, original_path)
            viewer.show()
