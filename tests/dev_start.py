import logging
import sys
from PyQt6.QtWidgets import QApplication

from src.gui.widgets.splash_screen import SplashScreen
from src.gui.windows.main_window import MainWindow
from src.util.logging import configure_root_logger

configure_root_logger(logging.INFO)

app = QApplication(sys.argv)
app.setQuitOnLastWindowClosed(True)

screen = SplashScreen()
screen.initial_setup()

window = MainWindow()
window.start(auto_new_job=True)

# Add some files to the selector
window.processing_pipeline.picker.file_list.file_list.add_items([
    r'D:\Documents\PycharmProjects\eagle-eye-qt\src\eagle-eye\form_templates\dev\test_kt_form__filled.jpg',
    r'D:\Documents\PycharmProjects\eagle-eye-qt\src\eagle-eye\form_templates\dev\test_kt_form__filled_errors.jpg',
])

# Pre-process
window.processing_pipeline.picker.confirm_files()
window.processing_pipeline.pre_processing.start_pre_processing()

app.exec()
