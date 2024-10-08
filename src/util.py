import logging
from typing import NamedTuple

UNSAFE_CHARACTERS = ['/', '.', ' ', '%']


class ApiSettings(NamedTuple):
    project_id: str
    access_token: str


def set_up_root_logger(verbose: bool) -> None:
    handler = logging.StreamHandler()
    handler.setFormatter(
        logging.Formatter(
            fmt='{asctime} | {levelname} | {filename} | {message}',
            style='{',
        )
    )

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG if verbose else logging.INFO)
    root_logger.addHandler(handler)


def sanitize_filename(name: str) -> str:
    clean_name = name.lower()
    for character in UNSAFE_CHARACTERS:
        clean_name = clean_name.replace(character, '_')
    return clean_name
