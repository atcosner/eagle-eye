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
    def jobs_directory() -> Path:
        return get_working_dir() / 'jobs'

    @staticmethod
    def job_directory(job_name: str) -> Path:
        return LocalPaths.jobs_directory() / job_name

    @staticmethod
    def input_files_directory(job_name: str) -> Path:
        return LocalPaths.job_directory(job_name) / 'input_files'

    @staticmethod
    def logs_directory() -> Path:
        return get_working_dir() / 'logs'

    @staticmethod
    def reference_forms_directory() -> Path:
        return get_working_dir() / 'reference_forms'

    @staticmethod
    def settings_file() -> Path:
        return get_working_dir() / 'settings.json'

    @staticmethod
    def database_file(primary: bool = True) -> Path:
        return get_working_dir() / ('primary.db' if primary else 'secondary.db')

    @staticmethod
    def set_up_job_directory(job_name: str) -> None:
        jobs_directory = LocalPaths.jobs_directory()
        jobs_directory.mkdir(exist_ok=True)

        top_directory = LocalPaths.job_directory(job_name)
        logger.info(f'Creating job directory: {top_directory}')
        top_directory.mkdir(exist_ok=True)

        input_file_dir = LocalPaths.input_files_directory(job_name)
        logger.info(f'Creating input file directory: {input_file_dir}')
        input_file_dir.mkdir(exist_ok=True)


