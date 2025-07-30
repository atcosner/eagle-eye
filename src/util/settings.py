import datetime
import logging
import json
from dataclasses import dataclass

from .paths import LocalPaths

logger = logging.getLogger(__name__)


class CustomEncoder(json.JSONEncoder):
    def default(self, obj: object) -> object:
        if isinstance(obj, (datetime.datetime, datetime.date)):
            return {'__custom_type__': 'date', 'value': obj.isoformat()}

        return super().default(obj)


class CustomDecoder(json.JSONDecoder):
    def __init__(self):
        super().__init__(object_hook=self.object_hook)

    def object_hook(self, obj):
        if '__custom_type__' in obj and 'value' in obj:
            match obj['__custom_type__']:
                case 'date':
                    try:
                        return datetime.date.fromisoformat(obj['value'])
                    except (ValueError, TypeError):
                        return obj
                case _:
                    return obj

        return obj


@dataclass
class SettingsManager:
    google_api_update_date: datetime.date | None = None
    google_project_id: str | None = None
    google_access_token: str | None = None

    # Members with a proceeding underscore are NOT written to disk

    def __post_init__(self):
        self.load()

    def __enter__(self) -> 'SettingsManager':
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.save()

    def valid_api_config(self) -> bool:
        return self.google_project_id is not None and self.google_access_token is not None

    def api_needs_update(self) -> bool:
        if self.google_api_update_date is None:
            return True
        else:
            current_date = datetime.date.today()
            return current_date != self.google_api_update_date

    def load(self) -> None:
        settings_file = LocalPaths.settings_file()
        logger.info(f'Loading settings: {settings_file}')

        if settings_file.is_file():
            with settings_file.open() as file:
                for key, value in json.load(file, cls=CustomDecoder).items():
                    if key in self.__dict__:
                        # logger.info(f'Setting "{key}" => "{value}"')
                        setattr(self, key, value)

    def save(self) -> None:
        settings_file = LocalPaths.settings_file()
        logger.info(f'Saving settings: {settings_file}')

        save_data = {}
        for member, value in self.__dict__.items():
            if not member.startswith('__') and not member.startswith('_') and not callable(getattr(self, member)):
                # logger.info(f'Saving: "{member}" = "{value}"')
                save_data[member] = value

        with settings_file.open('wt') as file:
            json.dump(save_data, file, cls=CustomEncoder)
