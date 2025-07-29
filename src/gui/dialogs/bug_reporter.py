import logging
import shutil
import uuid

from PyQt6.QtWidgets import QWidget, QDialog, QGroupBox, QVBoxLayout, QCheckBox, QHBoxLayout, QPushButton, QLabel

from src.gui.widgets.job.job_combo_box import JobComboBox
from src.gui.widgets.util.explorer_button import ExplorerButton
from src.gui.widgets.util.link_label import LinkLabel
from src.util.logging import get_current_logfile
from src.util.paths import LocalPaths

logger = logging.getLogger(__name__)


class BugReporter(QDialog):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setWindowTitle('Report An Issue')

        self.options_box = QGroupBox('Step 1 - Choose what to include in the report')
        # self.include_db = QCheckBox('Include Database')
        self.include_job_data = QCheckBox('Include Job Data')
        self.job_combo_box = JobComboBox()

        self.include_logs = QCheckBox('Include Logs')

        self.prep_button = QPushButton('Prepare')
        self.prep_button.pressed.connect(self.handle_prepare)

        self.submit_box = QGroupBox('Step 2 - File the bug report')

        self.close_button = QPushButton('Close')
        self.close_button.pressed.connect(self.reject)

        self._set_up_layout()
        self._initial_behavior()

    def _set_up_layout(self) -> None:
        job_data_layout = QHBoxLayout()
        job_data_layout.addWidget(self.include_job_data)
        job_data_layout.addWidget(self.job_combo_box)

        options_layout = QVBoxLayout()
        options_layout.addWidget(self.include_logs)
        # options_layout.addWidget(self.include_db)
        # TODO: allow the upload of job files
        # options_layout.addLayout(job_data_layout)
        self.options_box.setLayout(options_layout)

        prepare_button_layout = QHBoxLayout()
        prepare_button_layout.addStretch()
        prepare_button_layout.addWidget(self.prep_button)

        self.submit_layout = QVBoxLayout()
        self.submit_box.setLayout(self.submit_layout)

        close_button_layout = QHBoxLayout()
        close_button_layout.addStretch()
        close_button_layout.addWidget(self.close_button)

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.options_box)
        main_layout.addLayout(prepare_button_layout)
        main_layout.addWidget(self.submit_box)
        main_layout.addLayout(close_button_layout)
        self.setLayout(main_layout)

    def _initial_behavior(self) -> None:
        # force the user to include the logs
        self.include_logs.setChecked(True)
        self.include_logs.setDisabled(True)

        # disable the job button and combo box if there are no jobs
        if self.job_combo_box.count() == 0:
            self.include_job_data.setDisabled(True)
            self.job_combo_box.setDisabled(True)

    def handle_prepare(self) -> None:
        logger.info('Preparing bug report')

        # create a new directory for this report
        reports_base_dir = LocalPaths.bug_reports_directory()
        report_dir = reports_base_dir / str(uuid.uuid4())
        report_dir.mkdir()

        # add the issue link to the group box
        create_label = LinkLabel(
            r'1. Begin the issue creation process on '
            r'<a href="https://github.com/atcosner/eagle-eye/issues">GitHub</a>'
            r' using the <New issue> button and using the <Bug Report> template'
        )
        self.submit_layout.addWidget(create_label)

        # copy the log file into it and add a step
        new_path = report_dir / get_current_logfile().name
        logger.info(f'Copying {get_current_logfile()} -> {new_path}')
        shutil.copy2(get_current_logfile(), new_path)

        log_label = QLabel('2. Upload the following log file to the bug report')
        self.submit_layout.addWidget(log_label)

        log_layout = QHBoxLayout()
        log_layout.addWidget(QLabel('Look for the .log file in this directory: '))
        log_layout.addWidget(ExplorerButton(report_dir))
        self.submit_layout.addLayout(log_layout)

        # if we are including job files, zip them up
        if self.include_job_data.isChecked():
            job_id = self.job_combo_box.currentData()
            logger.info(f'Zipping files for job: {self.job_combo_box.currentText()} ({job_id})')
            # TODO: zip the job files

            job_label = QLabel('3. Upload the following job zip file to the bug report')
            self.submit_layout.addWidget(job_label)

            job_layout = QHBoxLayout()
            job_layout.addWidget(QLabel('Look for the .zip file in this directory: '))
            job_layout.addWidget(ExplorerButton(report_dir))
            self.submit_layout.addLayout(job_layout)
