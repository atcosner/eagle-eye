import logging
import subprocess

from PyQt6.QtCore import QSize, pyqtSlot
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QVBoxLayout, QLabel, QGroupBox, QPushButton, QHBoxLayout

from src.gui.widgets.util.link_label import LinkLabel
from src.util.resources import GENERIC_ICON_PATH

from ..util.base_page import BasePage
from ..util.dummy_field import DummyField

logger = logging.getLogger(__name__)


class CliInstallPage(BasePage):
    def __init__(self):
        super().__init__('Eagle Eye | Google Cloud CLI Install')

        self.step_box = QGroupBox('Install Google Cloud CLI')

        self.status_icon = QLabel()
        self.status_icon.setPixmap(QIcon(str(GENERIC_ICON_PATH / 'bad.png')).pixmap(QSize(20, 20)))

        self.status_label = QLabel('Google Cloud CLI is NOT installed')

        self.cli_installed = DummyField()
        self.registerField('cli.installed*', self.cli_installed, property='custom_value', changedSignal=self.cli_installed.valueChanged)

        self._set_up_layout()

    def _set_up_step(self) -> None:
        download_label = LinkLabel(
            r'Download and install the '
            r'<a href="https://cloud.google.com/sdk/docs/install-sdk">Google Cloud CLI</a>'
        )

        check_button = QPushButton('Check Install')
        check_button.pressed.connect(self.check_gcloud_cli_install)

        check_layout = QHBoxLayout()
        check_layout.addWidget(download_label)
        check_layout.addStretch()
        check_layout.addWidget(check_button)

        status_layout = QHBoxLayout()
        status_layout.addWidget(self.status_icon)
        status_layout.addWidget(self.status_label)
        status_layout.addStretch()

        layout = QVBoxLayout()
        layout.addLayout(check_layout)
        layout.addLayout(status_layout)
        self.step_box.setLayout(layout)

    def _set_up_layout(self) -> None:
        welcome_text = QLabel(
            'Eagle Eye uses the Google Cloud CLI to perform character recognition on submitted forms.\n'
            'Please follow the instructions below to install it'
        )
        margins = welcome_text.contentsMargins()
        margins.setBottom(10)
        welcome_text.setContentsMargins(margins)

        self._set_up_step()

        layout = QVBoxLayout()
        layout.addWidget(welcome_text)
        layout.addWidget(self.step_box)
        self.setLayout(layout)

    @pyqtSlot()
    def check_gcloud_cli_install(self) -> None:
        logger.info('Checking if gcloud is installed')

        found = False
        try:
            subprocess.run('gcloud version', shell=True, check=True, capture_output=True)

            logger.info('Command "gcloud version" ran successfully')
            icon_file_name = 'good.png'
            self.status_label.setText('Google Cloud CLI is installed')
            found = True

        except subprocess.CalledProcessError:
            logger.warning('Command "gcloud version" not found')
            icon_file_name = 'bad.png'
            self.status_label.setText('Google Cloud CLI is NOT installed')

        icon = QIcon(str(GENERIC_ICON_PATH / icon_file_name))
        self.status_icon.setPixmap(icon.pixmap(QSize(20, 20)))

        # update the wizard field
        self.cli_installed.set_value('Yes' if found else '')
