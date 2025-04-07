import logging
import os
import platform
from pathlib import Path

logger = logging.getLogger(__name__)


def get_user_data_dir() -> Path | None:
    system = platform.system()

    if system == 'Windows':
        return Path(os.getenv('LOCALAPPDATA'))

    logger.error(f'Unknown platform: "{system}"')
    return None


class LocalPaths:
    @staticmethod
    def log_directory() -> Path:
        return get_user_data_dir() / 'logs'

    @staticmethod
    def settings_file() -> Path:
        return get_user_data_dir() / 'settings.json'

    @staticmethod
    def primary_database_file() -> Path:
        return get_user_data_dir() / 'primary.db'

    @staticmethod
    def secondary_database_file() -> Path:
        return get_user_data_dir() / 'secondary.db'
