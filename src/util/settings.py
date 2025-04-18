import logging
import json
from dataclasses import dataclass

from .paths import LocalPaths

logger = logging.getLogger(__name__)


@dataclass
class SettingsManager:
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

    def load(self) -> None:
        settings_file = LocalPaths.settings_file()
        logger.info(f'Loading settings: {settings_file}')

        if settings_file.is_file():
            with settings_file.open() as file:
                for key, value in json.load(file).items():
                    if key in self.__dict__:
                        logger.info(f'Setting "{key}" => "{value}"')
                        setattr(self, key, value)

    def save(self) -> None:
        settings_file = LocalPaths.settings_file()
        logger.info(f'Saving settings: {settings_file}')

        save_data = {}
        for member, value in self.__dict__.items():
            if not member.startswith('__') and not member.startswith('_') and not callable(getattr(self, member)):
                logger.info(f'Saving: "{member}" = "{value}"')
                save_data[member] = value

        with settings_file.open('wt') as file:
            json.dump(save_data, file)
