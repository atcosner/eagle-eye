import sys

from PyQt6.QtWidgets import QApplication

from src.gui.windows.form_processing import FormProcessing


app = QApplication(sys.argv)

window = FormProcessing()
window.show()

app.exec()
