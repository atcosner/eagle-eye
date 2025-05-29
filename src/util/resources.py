from pathlib import Path

from PyQt6.QtGui import QIcon

RESOURCES_PATH = Path(__file__).parent / '..' / 'gui' / 'resources'

FILE_STATUS_ICON_PATH = RESOURCES_PATH / 'file_status'
FILE_TYPE_ICON_PATH = RESOURCES_PATH / 'file_type'
GENERIC_ICON_PATH = RESOURCES_PATH / 'generic'
REFERENCE_FORM_ICON_PATH = RESOURCES_PATH / 'reference_form'


def get_lock_icon(locked: bool) -> QIcon:
    return QIcon(str(GENERIC_ICON_PATH / ('lock.png' if locked else 'unlock.png')))
