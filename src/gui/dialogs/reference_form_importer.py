import logging
import sqlalchemy
from sqlalchemy.orm import Session

from PyQt6.QtCore import pyqtSlot, Qt
from PyQt6.QtWidgets import (
    QDialog, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QMessageBox, QFileDialog, QLineEdit, QLabel, QGroupBox,
)

from src.database import DB_ENGINE
from src.database.copy import copy_reference_form
from src.database.reference_form import ReferenceForm
from src.gui.widgets.reference_form.form_details_tree import FormDetailsTree

logger = logging.getLogger(__name__)


class ReferenceFormImporter(QDialog):
    def __init__(self, parent: QWidget | None):
        super().__init__(parent)
        self.setWindowTitle('Reference Form Importer')
        self.setMinimumWidth(600)

        self.step_one_box = QGroupBox('Step 1 - Select an Eagle Eye Database')

        self.db_path_edit = QLineEdit()
        self.db_path_edit.setReadOnly(True)

        self.select_button = QPushButton('Select')
        self.select_button.pressed.connect(self.handle_select_file)

        self.file_dialog = QFileDialog(self, 'Please select a database file')
        self.file_dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
        self.file_dialog.setViewMode(QFileDialog.ViewMode.Detail)
        self.file_dialog.setNameFilter('Eagle Eye DB (*.db)')

        self.step_two_box = QGroupBox('Step 2 - Select Reference Forms To Import')

        self.scan_db_button = QPushButton('Scan DB')
        self.scan_db_button.setDisabled(True)
        self.scan_db_button.pressed.connect(self.handle_scan_db)

        self.form_tree = FormDetailsTree(add_checkboxes=True)
        self.form_tree.setDisabled(True)

        self.import_button = QPushButton('Import')
        self.import_button.setDisabled(True)
        self.import_button.pressed.connect(self.handle_import_forms)

        self.close_button = QPushButton('Close')
        self.close_button.pressed.connect(self.close)

        self._db_session: Session | None = None

        self._set_up_layout()

    def _set_up_layout(self) -> None:
        file_layout = QHBoxLayout()
        file_layout.addWidget(QLabel('File Path:'))
        file_layout.addWidget(self.db_path_edit)
        file_layout.addWidget(self.select_button)
        self.step_one_box.setLayout(file_layout)

        scan_layout = QHBoxLayout()
        scan_layout.addWidget(self.scan_db_button)
        scan_layout.addStretch()

        import_layout = QHBoxLayout()
        import_layout.addStretch()
        import_layout.addWidget(self.import_button)

        select_layout = QVBoxLayout()
        select_layout.addLayout(scan_layout)
        select_layout.addWidget(self.form_tree)
        select_layout.addLayout(import_layout)
        self.step_two_box.setLayout(select_layout)

        close_layout = QHBoxLayout()
        close_layout.addStretch()
        close_layout.addWidget(self.close_button)

        layout = QVBoxLayout()
        layout.addWidget(self.step_one_box)
        layout.addWidget(self.step_two_box)
        layout.addLayout(close_layout)
        self.setLayout(layout)

    def establish_db_connection(self) -> Session | None:
        # TODO: catch exceptions and return None
        engine = sqlalchemy.create_engine(f'sqlite+pysqlite:///{self.db_path_edit.text()}', echo=False)
        return Session(engine)

    @pyqtSlot()
    def handle_import_forms(self) -> None:
        assert self._db_session is not None, 'Error DB session was not created'

        # get checked reference forms from the tree
        checked_forms = self.form_tree.get_checked_items()
        import_ids = [form.data(0, Qt.ItemDataRole.UserRole) for form in checked_forms]
        if not import_ids:
            QMessageBox.warning(self, 'Selection Error', 'Please select at least one form.')
            return

        # import each of the IDs into the current database
        with Session(DB_ENGINE) as new_session:
            for old_form_id in import_ids:
                old_form = self._db_session.get(ReferenceForm, old_form_id)

                new_form = ReferenceForm('', None, 0, None)
                # TODO: the DB does not have the reference image file only a path to it
                copy_reference_form(new_form, old_form, copy_details=True)
                new_session.add(new_form)
                new_session.commit()

        # display success
        QMessageBox.information(
            self,
            'Import Success',
            f'Successfully imported {len(import_ids)} reference form(s)',
        )
        self.accept()

    @pyqtSlot()
    def handle_scan_db(self) -> None:
        self.select_button.setDisabled(True)

        # establish the DB connection
        db_session = self.establish_db_connection()
        if db_session is None:
            QMessageBox.critical(self, 'Database Read Error', 'Error reading the database file')
            return

        # TODO: check the DB version against our own (don't allow import if the version is mismatched)
        self._db_session = db_session

        # load the form tree
        self.form_tree.load_reference_forms(db_session)
        self.form_tree.setDisabled(False)

        # enable the import button
        self.import_button.setDisabled(False)

    @pyqtSlot()
    def handle_select_file(self) -> None:
        if self.file_dialog.exec():
            # update the line edit
            file_path = self.file_dialog.selectedFiles()[0]
            self.db_path_edit.setText(file_path)

            # enable the scan DB button
            self.scan_db_button.setDisabled(False)
