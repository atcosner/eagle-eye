from enum import Enum

from PyQt6.QtGui import QIcon, QMovie

from .resources import FILE_STATUS_ICON_PATH


class FileStatus(Enum):
    PENDING = object()
    IN_PROGRESS = object()
    SUCCESS = object()
    FAILED = object()
    WARNING = object()


def get_icon_for_status(status: FileStatus) -> QIcon | QMovie:
    match status:
        case FileStatus.PENDING:
            return QIcon(str(FILE_STATUS_ICON_PATH / 'file_pending.png'))
        case FileStatus.IN_PROGRESS:
            return QMovie(str(FILE_STATUS_ICON_PATH / 'progress.gif'))
        case FileStatus.SUCCESS:
            return QIcon(str(FILE_STATUS_ICON_PATH / 'file_success.png'))
        case FileStatus.FAILED:
            return QIcon(str(FILE_STATUS_ICON_PATH / 'file_error.png'))
        case FileStatus.WARNING:
            return QIcon(str(FILE_STATUS_ICON_PATH / 'file_warning.png'))
        case _:
            raise Exception(f'Unknown status: {status}')


def is_finished(status: FileStatus) -> bool:
    return status in (FileStatus.SUCCESS, FileStatus.FAILED, FileStatus.WARNING)
