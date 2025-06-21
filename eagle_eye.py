import logging
import sys
from PyQt6.QtWidgets import QApplication

from src.gui.widgets.splash_screen import SplashScreen
from src.gui.windows.main_window import MainWindow
from src.util.logging import configure_root_logger

configure_root_logger(logging.INFO)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(True)

    screen = SplashScreen()
    screen.initial_setup()

    window = MainWindow()
    window.start()

    app.exec()
