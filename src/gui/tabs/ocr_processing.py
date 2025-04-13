from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout

from ..widgets.file_status_list import FileStatusList, FileStatusItem


class OcrProcessing(QWidget):
    def __init__(self):
        super().__init__()
        self._job_db_id: int | None = None

        self.status_list = FileStatusList()
        # self.status_list.currentItemChanged.connect(self.selected_file_changed)

        self._set_up_layout()

    def _set_up_layout(self) -> None:
        layout = QVBoxLayout()
        layout.addWidget(self.status_list)
        # layout.addWidget(self.details)

        # button_layout = QHBoxLayout()
        # button_layout.addStretch()
        # button_layout.addWidget(self.auto_process)
        # button_layout.addWidget(self.process_file_button)
        # layout.addLayout(button_layout)

        self.setLayout(layout)
