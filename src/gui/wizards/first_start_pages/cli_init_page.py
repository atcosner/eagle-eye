import logging
import subprocess

from PyQt6.QtCore import QSize, pyqtSlot
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QVBoxLayout, QLabel, QGroupBox, QPushButton, QHBoxLayout

from src.gui.widgets.util.link_label import LinkLabel
from src.gui.widgets.util.log_viewer import LogViewer
from src.util.resources import GENERIC_ICON_PATH

from ..util.base_page import BasePage
from ..util.dummy_field import DummyField

logger = logging.getLogger(__name__)


class CliInitPage(BasePage):
    def __init__(self):
        super().__init__('Eagle Eye | Google Cloud CLI Initialization')

        self.step_box = QGroupBox('Initialization Google Cloud CLI')

        self.log_viewer = LogViewer()

        self.status_icon = QLabel()
        self.status_icon.setPixmap(QIcon(str(GENERIC_ICON_PATH / 'bad.png')).pixmap(QSize(20, 20)))

        self.status_label = QLabel('Google Cloud CLI is NOT initialized')

        self.cli_init = DummyField()
        self.registerField('cli.init*', self.cli_init, property='custom_value', changedSignal=self.cli_init.valueChanged)

        self._set_up_layout()

    def _set_up_step(self) -> None:
        init_label = LinkLabel(
            r'Initialize the '
            r'<a href="https://docs.cloud.google.com/sdk/docs/install-sdk#initializing-the-cli">Google Cloud CLI</a>'
        )

        check_button = QPushButton('Check Initialization')
        check_button.pressed.connect(self.check_gcloud_cli_initialization)

        check_layout = QHBoxLayout()
        check_layout.addWidget(init_label)
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
            'The Google Cloud CLI must be authorized and configured to use the project you created.\n'
            'Please follow the instructions below to initialize it'
        )
        margins = welcome_text.contentsMargins()
        margins.setBottom(10)
        welcome_text.setContentsMargins(margins)

        self._set_up_step()

        layout = QVBoxLayout()
        layout.addWidget(welcome_text)
        layout.addWidget(self.step_box)
        layout.addWidget(QLabel('Logs'))
        layout.addWidget(self.log_viewer)
        self.setLayout(layout)

    @pyqtSlot()
    def check_gcloud_cli_initialization(self) -> None:
        logger.info('Checking if gcloud is initialized')

        init_done = False
        try:
            cmd = 'gcloud config configurations list'
            self.log_viewer.add_line(f'Running: {cmd}')
            self.log_viewer.add_line('')

            output = subprocess.run(
                cmd,
                shell=True,
                check=True,
                capture_output=True,
                text=True,
            )

            logger.info('Output:')
            logger.info(output.stdout)

            self.log_viewer.add_line('Output:')
            self.log_viewer.add_lines(output.stdout)

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
                init_done = True
            else:
                icon_file_name = 'bad.png'

        except subprocess.CalledProcessError:
            # gcloud CLI is not installed
            icon_file_name = 'bad.png'

        icon = QIcon(str(GENERIC_ICON_PATH / icon_file_name))
        self.status_icon.setPixmap(icon.pixmap(QSize(20, 20)))

        self.cli_init.set_value('Yes' if init_done else '')
