import logging
import sys
from PyQt6.QtWidgets import QApplication, QMainWindow

from src.gui.widgets.file_preview import FilePreview
from src.util.logging import configure_root_logger

configure_root_logger(logging.INFO)

app = QApplication(sys.argv)
app.setQuitOnLastWindowClosed(True)

file_preview = FilePreview()

window = QMainWindow()
window.setCentralWidget(file_preview)
window.resize(600, 900)
window.show()

file_preview.update_preview(r"D:\Documents\PycharmProjects\eagle-eye-qt\src\eagle-eye\form_templates\dev\test_kt_form__filled.jpg")

app.exec()
