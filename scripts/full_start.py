import argparse
import logging
import sys
from PyQt6.QtWidgets import QApplication

from src.gui.widgets.splash_screen import SplashScreen
from src.gui.windows.main_window import MainWindow
from src.util.logging import configure_root_logger, log_uncaught_exception

configure_root_logger(logging.INFO)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument('--no-splash', action='store_true', help='Skip displaying the splash screen')
    parser.add_argument('--load-last-job', action='store_true', help='Load the most recent job')

    return parser.parse_args()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(True)

    # overwire the default exception handler
    sys.excepthook = log_uncaught_exception

    args = parse_args()

    if not args.no_splash:
        screen = SplashScreen()
        screen.initial_setup()

    window = MainWindow()
    window.start(
        load_latest_job=args.load_last_job,
    )

    app.exec()
