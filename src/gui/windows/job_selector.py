from PyQt6.QtCore import pyqtSlot
from PyQt6.QtWidgets import QRadioButton, QVBoxLayout, QLabel, QWidget, QHBoxLayout

from .base import BaseWindow


class JobSelector(BaseWindow):
    def __init__(self):
        super().__init__('Job Selection')

        self.new_job_button = QRadioButton('Create a new job', self)
        self.existing_job_button = QRadioButton('Continue an existing job', self)

        self.new_job_button.setChecked(True)
        self.existing_job_button.pressed.connect(self.toggle_job_list_visibility)

        self._set_up_layout()

    def _set_up_layout(self) -> None:
        layout = QVBoxLayout()
        layout.addWidget(self.new_job_button)

        divider_layout = QHBoxLayout()
        divider_layout.addStretch()
        divider_layout.addWidget(QLabel('- OR -'))
        divider_layout.addStretch()
        layout.addLayout(divider_layout)

        layout.addWidget(self.existing_job_button)

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

    @pyqtSlot
    def toggle_job_list_visibility(self) -> None:
        pass
