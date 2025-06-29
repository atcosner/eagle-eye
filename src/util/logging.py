import logging
import sys
from contextlib import contextmanager
from datetime import datetime
from types import TracebackType
from typing import Any, Type, Callable

from .paths import LocalPaths

logger = logging.getLogger(__name__)

LOG_WIDTH = 120


class NamedLoggerAdapter(logging.LoggerAdapter):
    def __init__(self, log: logging.Logger, name: Any):
        super().__init__(log, {'name': str(name)})

    def process(self, msg, kwargs):
        return f'[{self.extra["name"]}] | {msg}', kwargs


@contextmanager
def log_block(log_func: Callable, block_name: str) -> None:
    half_width = (LOG_WIDTH - len(block_name) - 2) // 2
    log_func(f'{"-" * half_width} {block_name} {"-" * half_width}')
    try:
        yield
    finally:
        log_func('-' * LOG_WIDTH)
        log_func('')


def configure_root_logger(min_level: int) -> None:
    log_file = LocalPaths.logs_directory() / f'eagle_eye_{datetime.now():%Y%m%d_%H%M%S}.log'

    logging.basicConfig(
        format='%(asctime)s | %(levelname)s | %(name)s | %(message)s',
        level=min_level,
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(log_file),
        ],
    )


def log_uncaught_exception(
        exc_type: Type[BaseException],
        exc_value: BaseException,
        exc_traceback: TracebackType,
) -> None:
    logger.critical('Uncaught exception', exc_info=(exc_type, exc_value, exc_traceback))

    # Pass the exception to the default handler
    sys.__excepthook__(exc_type, exc_value, exc_traceback)
