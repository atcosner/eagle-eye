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

# screen = SplashScreen()
# screen.initial_setup()

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

#
# DEVELOPMENT TESTING FILES
#
DEV_PATH = project_path / 'scripts' / 'test_files'
TEST_FILES = [
    # use forms with real data
    # DEV_PATH / 'kt' / '40013-40014.jpg',
    # DEV_PATH / 'kt' / '40015-40018.pdf',
    DEV_PATH / 'fn' / 'FN5007.pdf',

    # # pdf with alignment errors
    # DEV_PATH / 'kt' / '40013-40018.pdf',

    # # fake testing forms
    # DEV_PATH / 'kt' / 'test_kt_form__filled.jpg',
    # DEV_PATH / 'kt' / 'test_kt_form__filled_errors.jpg',
]

# Add some files to the selector
window.job_widget.processing_pipeline.picker.file_list.file_list.add_items(TEST_FILES)

# Choose the reference form based on the test files were using
found_form = False
reference_form_prefix = TEST_FILES[0].parent.name.upper()
for index in range(window.job_widget.reference_form_selector.count()):
    form_name = window.job_widget.reference_form_selector.itemText(index)
    print(f'Checking: {form_name}')

    if reference_form_prefix in form_name:
        print(f'Selected reference form: {form_name}')
        window.job_widget.reference_form_selector.setCurrentIndex(index)
        found_form = True

if not found_form:
    assert False, f'Did not find reference form that contained: {reference_form_prefix}'

# Pre-process
window.job_widget.processing_pipeline.picker.continueToNextStep.emit()
window.job_widget.processing_pipeline.pre_processing.start_processing()

app.exec()
