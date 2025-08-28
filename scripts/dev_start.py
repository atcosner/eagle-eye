import logging
import sys
from pathlib import Path
from PyQt6.QtWidgets import QApplication

from src.gui.widgets.splash_screen import SplashScreen
from src.gui.windows.main_window import MainWindow
from src.util.logging import configure_root_logger, log_uncaught_exception

configure_root_logger(logging.INFO)

app = QApplication(sys.argv)
app.setQuitOnLastWindowClosed(True)

# overwire the default exception handler
sys.excepthook = log_uncaught_exception

screen = SplashScreen()
screen.initial_setup()

window = MainWindow()
window.start(auto_new_job=True)

# Determine the location of the project directory
file_path = Path(__file__)
project_path = None
for parent in file_path.parents:
    if parent.name == 'eagle-eye':
        project_path = parent
        break
print(f'Project path: {project_path}')
assert project_path is not None

# Add some files to the selector
dev_path = project_path / 'scripts' / 'test_files'
window.job_widget.processing_pipeline.picker.file_list.file_list.add_items([
    # use forms with real data
    dev_path / 'kt' / '40013-40014.jpg',
    # dev_path / 'kt' / '40015-40018.pdf',

    # # pdf with alignment errors
    # dev_path / 'kt' / '40013-40018.pdf',

    # # fake testing forms
    # dev_path / 'kt' / 'test_kt_form__filled.jpg',
    # dev_path / 'kt' / 'test_kt_form__filled_errors.jpg',
])

# Pre-process
window.job_widget.processing_pipeline.picker.continueToNextStep.emit()
window.job_widget.processing_pipeline.pre_processing.start_processing()

app.exec()
