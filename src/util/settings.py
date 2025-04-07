import logging
import json
from dataclasses import dataclass

from .paths import LocalPaths

logger = logging.getLogger(__name__)


@dataclass
class SettingsManager:
    test: int

    # Members with a proceeding underscore are NOT written to disk

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
        pass
