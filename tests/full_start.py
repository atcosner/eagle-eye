import sys
from PyQt6.QtWidgets import QApplication

from src.gui.windows.job_selector import JobSelector


app = QApplication(sys.argv)

window = JobSelector()
window.show()

app.exec()
