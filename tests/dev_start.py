import logging
import sys
from PyQt6.QtWidgets import QApplication

from src.gui.windows.main_window import MainWindow
from src.util.logging import configure_root_logger

configure_root_logger(logging.INFO)

app = QApplication(sys.argv)
app.setQuitOnLastWindowClosed(True)

window = MainWindow()
window.start(auto_new_job=True)

# Add some files to the selector
window.processing_pipeline.picker.file_list.file_list.add_items([
    r'D:\Documents\PycharmProjects\eagle-eye-qt\src\eagle-eye\form_templates\dev\test_kt_form__filled.jpg',
    r'D:\Documents\PycharmProjects\eagle-eye-qt\src\eagle-eye\form_templates\dev\test_kt_form__filled_errors.jpg',
])

# Move them to pre-processing
window.processing_pipeline.picker.confirm_files()
window.processing_pipeline.setCurrentIndex(1)

app.exec()
