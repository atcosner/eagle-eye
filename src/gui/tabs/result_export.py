import logging
from pathlib import Path
from sqlalchemy.orm import Session

from PyQt6.QtCore import pyqtSlot
from PyQt6.QtWidgets import (
    QWidget, QComboBox, QLineEdit, QPushButton, QHBoxLayout, QLabel, QGroupBox,
    QRadioButton, QVBoxLayout, QTextEdit, QMessageBox, QFileDialog,
)

from src.database import DB_ENGINE
from src.database.job import Job
from src.processing.export import get_mode_explanation, build_export_df
from src.util.export import ExportMode

logger = logging.getLogger(__name__)


class ModeButton(QRadioButton):
    def __init__(self, mode: ExportMode):
        self._mode = mode
        super().__init__(mode.name.capitalize())

    def get_mode(self) -> ExportMode:
        return self._mode


#
# TODO: This should be extensible for more than 2 export formats (stop assuming CSV and Excel are the only choices)
#


class ResultExport(QWidget):
    def __init__(self):
        super().__init__()
        self._job_db_id: int | None = None

        self.export_formats = QComboBox()
        self.export_file_path = QLineEdit()
        self.export_browse_button = QPushButton('Browse')
        self.export_option_group = QGroupBox('Export Mode')
        self.export_button = QPushButton('Export')

        self.strict_mode_button = ModeButton(ExportMode.STRICT)
        self.moderate_mode_button = ModeButton(ExportMode.MODERATE)
        self.full_mode_button = ModeButton(ExportMode.FULL)
        self.mode_explanation = QTextEdit()

        self._set_up_layout()
        self._set_defaults()

    def _set_defaults(self) -> None:
        self.export_formats.clear()
        self.export_formats.addItems(['CSV (.csv)', 'Excel (.xslx)'])
        self.export_formats.currentTextChanged.connect(self.handle_export_format_change)

        self.export_file_path.setReadOnly(True)
        self.export_browse_button.pressed.connect(self.handle_browse_file)

        self.mode_explanation.setReadOnly(True)
        self.mode_explanation.setMaximumHeight(100)
        self.mode_explanation.setMinimumWidth(200)
        self.mode_explanation.setAcceptRichText(True)

        self.strict_mode_button.clicked.connect(self.handle_mode_clicked)
        self.moderate_mode_button.clicked.connect(self.handle_mode_clicked)
        self.full_mode_button.clicked.connect(self.handle_mode_clicked)

        # TODO: This choice should be a user setting
        self.full_mode_button.setChecked(True)
        self.handle_mode_clicked()

        self.export_button.pressed.connect(self.handle_export_results)

    def _set_up_layout(self) -> None:
        export_format_layout = QHBoxLayout()
        export_format_layout.addWidget(QLabel('Output File Format:'))
        export_format_layout.addWidget(self.export_formats)
        export_format_layout.addStretch()

        export_file_path_layout = QHBoxLayout()
        export_file_path_layout.addWidget(QLabel('Output File Path:'))
        export_file_path_layout.addWidget(self.export_file_path)
        export_file_path_layout.addWidget(self.export_browse_button)
        export_file_path_layout.addStretch()

        mode_button_layout = QVBoxLayout()
        mode_button_layout.addWidget(self.strict_mode_button)
        mode_button_layout.addWidget(self.moderate_mode_button)
        mode_button_layout.addWidget(self.full_mode_button)
        self.export_option_group.setLayout(mode_button_layout)

        mode_layout = QHBoxLayout()
        mode_layout.addWidget(self.export_option_group)
        mode_layout.addWidget(self.mode_explanation)

        layout = QVBoxLayout()
        layout.addLayout(export_format_layout)
        layout.addLayout(export_file_path_layout)
        layout.addLayout(mode_layout)
        layout.addWidget(self.export_button)
        layout.addStretch()
        self.setLayout(layout)

    def load_job(self, job: Job | int | None) -> None:
        self._job_db_id = None
        if job is None:
            return

        self._job_db_id = job if isinstance(job, int) else job.id
        with Session(DB_ENGINE) as session:
            job = session.get(Job, job) if isinstance(job, int) else job

            # Try and put the file on the desktop
            home_path = Path.home()
            if (home_path / 'Desktop').exists():
                home_path = home_path / 'Desktop'

            path = home_path / f'{job.name}_export{self.get_file_filter()[0]}'
            self.export_file_path.setText(str(path))

    def get_file_filter(self) -> tuple[str, str]:
        selected = self.export_formats.currentText()
        if 'csv' in selected:
            return '.csv', 'Comma-Separated-Values (*.csv)'
        else:
            return '.xslx', 'Excel Workbook (*.xslx)'

    def get_export_mode(self) -> ExportMode:
        if self.strict_mode_button.isChecked():
            return self.strict_mode_button.get_mode()
        elif self.moderate_mode_button.isChecked():
            return self.moderate_mode_button.get_mode()
        else:
            return self.full_mode_button.get_mode()

    @pyqtSlot(str)
    def handle_export_format_change(self, new_format: str) -> None:
        current_path = Path(self.export_file_path.text())
        new_path = current_path.with_suffix('.csv' if 'csv' in new_format else '.xlsx')
        self.export_file_path.setText(str(new_path))

    @pyqtSlot()
    def handle_browse_file(self) -> None:
        file_path, _ = QFileDialog.getSaveFileName(
            parent=self,
            caption='Save Export File',
            directory=self.export_file_path.text(),
            filter=self.get_file_filter()[1],
        )

        if file_path:
            self.export_file_path.setText(file_path)

    @pyqtSlot()
    def handle_mode_clicked(self) -> None:
        self.mode_explanation.setText(get_mode_explanation(self.get_export_mode()))

    @pyqtSlot()
    def handle_export_results(self) -> None:
        # Ensure we have a file path
        if not self.export_file_path.text():
            QMessageBox.critical(
                self,
                'Export Error',
                'No file name selected.'
            )
            return

        # Load the job and turn it into a dataframe
        assert self._job_db_id, 'Cannot export without a job id'
        with Session(DB_ENGINE) as session:
            job = session.get(Job, self._job_db_id)
            export_df = build_export_df(self.get_export_mode(), job)

        # Export the dataframe in the requested format
        if 'csv' in self.export_formats.currentText():
            # CSV
            export_df.to_csv(self.export_file_path.text())
        else:
            # XLSX
            export_df.to_excel(self.export_file_path.text())
