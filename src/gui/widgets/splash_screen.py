import logging
import time

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QSplashScreen

from src.database import DB_ENGINE, OrmBase, read_db_version
from src.database.version import DB_VERSION
from src.util.google_api import save_api_settings
from src.util.paths import LocalPaths
from src.util.settings import SettingsManager
from src.util.resources import RESOURCES_PATH

logger = logging.getLogger(__name__)


class SplashScreen(QSplashScreen):
    def __init__(self):
        # Scale the icon to an appropriate size
        main_icon = QPixmap(str(RESOURCES_PATH / 'splash_screen.png'))
        super().__init__(
            main_icon.scaled(
                600,
                200,
                aspectRatioMode=Qt.AspectRatioMode.KeepAspectRatio,
                transformMode=Qt.TransformationMode.SmoothTransformation,
            )
        )

    def initial_setup(self) -> None:
        self.show()
        time.sleep(2)

        # Create the DB if we don't have one
        if not LocalPaths.database_file().exists():
            self.showMessage(
                'Creating primary database',
                Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignRight,
            )
            OrmBase.metadata.create_all(DB_ENGINE)
            time.sleep(2)
            self.clearMessage()

        # TODO: If I add DB revisions, this is where I should update the DB
        local_db_version = read_db_version(DB_ENGINE)
        if local_db_version != DB_VERSION:
            logger.warning(f'DB version mismatch! Local: {local_db_version}, Expected: {DB_VERSION}')

        # Update the Google API project and auth key
        settings = SettingsManager()
        if settings.valid_api_config() and settings.api_needs_update():
            self.showMessage(
                'Updating Google API Config',
                Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignRight,
            )
            save_api_settings()
            self.clearMessage()

        self.close()
