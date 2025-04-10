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


def get_working_dir() -> Path | None:
    work_dir = get_user_data_dir() / 'EagleEye'
    work_dir.mkdir(exist_ok=True)

    return work_dir


class LocalPaths:
    @staticmethod
    def log_directory() -> Path:
        return get_working_dir() / 'logs'

    @staticmethod
    def reference_form_directory() -> Path:
        return get_working_dir() / 'reference_forms'

    @staticmethod
    def settings_file() -> Path:
        return get_working_dir() / 'settings.json'

    @staticmethod
    def database_file(primary: bool = True) -> Path:
        return get_working_dir() / ('primary.db' if primary else 'secondary.db')
