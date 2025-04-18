import logging
import subprocess

from PyQt6.QtCore import pyqtSlot, QSize
from PyQt6.QtGui import QIcon, QCloseEvent
from PyQt6.QtWidgets import QWidget, QGroupBox, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QMessageBox

from src.util.google_api import save_api_settings
from src.util.resources import GENERIC_ICON_PATH

from .base import BaseWindow
from ..widgets.link_label import LinkLabel

logger = logging.getLogger(__name__)


class VisionApiConfig(BaseWindow):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent, 'Google Vision API Config')
        self._gcloud_installed: bool = False
        self._gcloud_initialized: bool = False

        self.step_one_box = QGroupBox('Step 1 - Create a Google Could Project and Enable Billing')

        self.step_two_box = QGroupBox('Step 2 - Install Google Cloud CLI')
        self.cli_status_icon = QLabel()
        self.cli_status_label = QLabel()
        self.cli_check_button = QPushButton('Check Install')
        self.cli_check_button.pressed.connect(self.check_gcloud_cli_install)

        self.step_three_box = QGroupBox('Step 3 - Initialize the Google Cloud CLI')
        self.init_status_icon = QLabel()
        self.init_status_label = QLabel()
        self.init_button = QPushButton('Initialize')
        self.init_button.pressed.connect(self.start_gcloud_cli_initialization)
        self.init_check_button = QPushButton('Check Initialization')
        self.init_check_button.pressed.connect(self.check_gcloud_cli_initialization)

        self.close_button = QPushButton('Close')
        self.close_button.pressed.connect(self.close)

        self._set_up_layout()
        self.check_gcloud_cli_install()
        self.check_gcloud_cli_initialization()

    def _set_up_step_one(self) -> None:
        project_label = LinkLabel(
            r'1. Ensure you have created a '
            r'<a href="https://developers.google.com/workspace/guides/create-project">Google Could Project</a>'
        )
        billing_label = LinkLabel(
            '2. Ensure you have enabled '
            '<a href="https://cloud.google.com/billing/docs/how-to/modify-project#enable_billing_for_a_project">Billing</a> '
            'in your Google Could Project'
        )

        step_one_layout = QVBoxLayout()
        step_one_layout.addWidget(project_label)
        step_one_layout.addWidget(billing_label)
        self.step_one_box.setLayout(step_one_layout)

    def _set_up_step_two(self) -> None:
        download_label = LinkLabel(
            r'1. Download and install the '
            r'<a href="https://cloud.google.com/sdk/docs/install-sdk">Google Could CLI</a>'
        )

        status_layout = QHBoxLayout()
        status_layout.addWidget(self.cli_status_icon)
        status_layout.addWidget(self.cli_status_label)
        status_layout.addStretch()
        status_layout.addWidget(self.cli_check_button)

        step_two_layout = QVBoxLayout()
        step_two_layout.addWidget(download_label)
        step_two_layout.addLayout(status_layout)
        self.step_two_box.setLayout(step_two_layout)

    def _set_up_step_three(self) -> None:
        status_layout = QHBoxLayout()
        status_layout.addWidget(self.init_status_icon)
        status_layout.addWidget(self.init_status_label)
        status_layout.addStretch()
        status_layout.addWidget(self.init_check_button)

        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(self.init_button)

        step_three_layout = QVBoxLayout()
        step_three_layout.addLayout(status_layout)
        step_three_layout.addLayout(button_layout)
        self.step_three_box.setLayout(step_three_layout)

        self.init_check_button.setDisabled(True)

    def _set_up_layout(self) -> None:
        self._set_up_step_one()
        self._set_up_step_two()
        self._set_up_step_three()

        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(self.close_button)

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.step_one_box)
        main_layout.addWidget(self.step_two_box)
        main_layout.addWidget(self.step_three_box)
        main_layout.addLayout(button_layout)

        widget = QWidget()
        widget.setLayout(main_layout)
        self.setCentralWidget(widget)

    def closeEvent(self, event: QCloseEvent) -> None:
        if self._gcloud_installed and self._gcloud_initialized:
            save_api_settings()
            event.accept()
        else:
            result = QMessageBox.warning(
                self,
                'Conform Close',
                'Are you sure you want to close the Google Vision API Config?\n'
                'OCR will be unavailable until you complete the three setup steps',
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )
            if result == QMessageBox.StandardButton.Yes:
                event.accept()
            else:
                event.ignore()

    def update_close_button(self) -> None:
        if not self._gcloud_installed or not self._gcloud_initialized:
            # Display the caution icon
            self.close_button.setIcon(QIcon(str(GENERIC_ICON_PATH / 'warning.png')))
            self.close_button.setToolTip('OCR will be unavailable until all steps are completed')
        else:
            # Display the good icon
            self.close_button.setIcon(QIcon(str(GENERIC_ICON_PATH / 'good.png')))
            self.close_button.setToolTip(None)

        self.close_button.setIconSize(QSize(15, 15))

    @pyqtSlot()
    def check_gcloud_cli_install(self) -> None:
        logger.info('Checking if gcloud is installed')

        try:
            subprocess.run('gcloud version', shell=True, check=True, capture_output=True)

            logger.info('Command "gcloud version" ran successfully')
            icon_file_name = 'good.png'
            self.cli_status_label.setText('The Google Cloud CLI was detected')
            self._gcloud_installed = True
        except subprocess.CalledProcessError:
            logger.warning('Command "gcloud version" not found')
            icon_file_name = 'bad.png'
            self.cli_status_label.setText('The Google Cloud CLI is not installed')
            self._gcloud_installed = False

        icon = QIcon(str(GENERIC_ICON_PATH / icon_file_name))
        self.cli_status_icon.setPixmap(icon.pixmap(QSize(20, 20)))

        self.update_close_button()

        if self._gcloud_installed:
            logger.info('Moving to step 3')
            self.cli_check_button.setDisabled(True)
            self.init_check_button.setDisabled(False)

    @pyqtSlot()
    def check_gcloud_cli_initialization(self) -> None:
        logger.info('Checking if gcloud is initialized')

        try:
            output = subprocess.run(
                'gcloud config configurations list',
                shell=True,
                check=True,
                capture_output=True,
                text=True,
            )

            found_complete_config = False
            for line in output.stdout.splitlines():
                # NAME     IS_ACTIVE  ACCOUNT  PROJECT  COMPUTE_DEFAULT_ZONE  COMPUTE_DEFAULT_REGION
                # default  True
                parts = line.split()
                if parts[1] == 'True':
                    logger.info(f'Found active config: "{line}"')
                    found_complete_config = True if len(parts) >= 4 else False

            if found_complete_config:
                icon_file_name = 'good.png'
                self.init_status_label.setText('The Google Cloud CLI has been initialized')
                self._gcloud_initialized = True
                self.init_button.setVisible(False)
            else:
                icon_file_name = 'bad.png'
                self.init_status_label.setText('Please initialize the Google Cloud CLI')
                self._gcloud_initialized = False
                self.init_button.setVisible(True)

        except subprocess.CalledProcessError:
            # gcloud CLI is not installed
            icon_file_name = 'bad.png'
            self.init_status_label.setText('Please complete Step 2 first')
            self._gcloud_initialized = False

        self.update_close_button()

        icon = QIcon(str(GENERIC_ICON_PATH / icon_file_name))
        self.init_status_icon.setPixmap(icon.pixmap(QSize(20, 20)))

        if self._gcloud_initialized:
            logger.info('Completed initialization')
            self.init_check_button.setDisabled(True)

    @pyqtSlot()
    def start_gcloud_cli_initialization(self) -> None:
        # TODO: Handle other operating systems
        subprocess.run('start /wait gcloud init', shell=True)
        self.check_gcloud_cli_initialization()

    def get_overall_status(self) -> bool:
        self.check_gcloud_cli_install()
        self.check_gcloud_cli_initialization()
        return self._gcloud_installed and self._gcloud_initialized
