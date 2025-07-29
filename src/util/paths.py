import logging
import os
import platform
import shutil
import uuid
from pathlib import Path

logger = logging.getLogger(__name__)


def is_pdf(path: Path) -> bool:
    # TODO: is there a better way?
    return path.suffix == '.pdf'


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


def safe_dir_delete(path: Path) -> None:
    try:
        shutil.rmtree(path)
    except (shutil.Error, FileNotFoundError):
        logger.exception(f'Failed to remove {path}')


class LocalPaths:
    @staticmethod
    def jobs_directory() -> Path:
        return get_working_dir() / 'jobs'

    @staticmethod
    def job_directory(job_uuid: uuid.UUID) -> Path:
        return LocalPaths.jobs_directory() / str(job_uuid)

    @staticmethod
    def input_files_directory(job_uuid: uuid.UUID) -> Path:
        return LocalPaths.job_directory(job_uuid) / 'input_files'

    @staticmethod
    def input_file_directory(job_uuid: uuid.UUID, file_id: int) -> Path:
        return LocalPaths.input_files_directory(job_uuid) / str(file_id)

    @staticmethod
    def pre_processing_directory(job_uuid: uuid.UUID, file_id: int) -> Path:
        return LocalPaths.input_file_directory(job_uuid, file_id) / 'pre_processing'

    @staticmethod
    def processing_directory(job_uuid: uuid.UUID, file_id: int) -> Path:
        return LocalPaths.input_file_directory(job_uuid, file_id) / 'processing'

    @staticmethod
    def logs_directory() -> Path:
        log_dir = get_working_dir() / 'logs'
        log_dir.mkdir(exist_ok=True)
        return log_dir

    @staticmethod
    def reference_forms_directory() -> Path:
        return get_working_dir() / 'reference_forms'

    @staticmethod
    def bug_reports_directory() -> Path:
        reports_dir = get_working_dir() / 'bug_reports'
        reports_dir.mkdir(exist_ok=True)
        return reports_dir

    @staticmethod
    def settings_file() -> Path:
        return get_working_dir() / 'settings.json'

    @staticmethod
    def database_file(primary: bool = True) -> Path:
        return get_working_dir() / ('primary.db' if primary else 'secondary.db')

    @staticmethod
    def set_up_job_directory(job_uuid: uuid.UUID) -> None:
        jobs_directory = LocalPaths.jobs_directory()
        jobs_directory.mkdir(exist_ok=True)

        top_directory = LocalPaths.job_directory(job_uuid)
        logger.info(f'Creating job directory: {top_directory}')
        top_directory.mkdir(exist_ok=True)

        input_file_dir = LocalPaths.input_files_directory(job_uuid)
        logger.info(f'Creating input file directory: {input_file_dir}')
        input_file_dir.mkdir(exist_ok=True)
