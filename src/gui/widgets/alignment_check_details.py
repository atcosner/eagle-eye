import logging
from sqlalchemy.orm import Session

from PyQt6.QtWidgets import QFrame, QLabel, QLineEdit, QGridLayout

from src.database import DB_ENGINE
from src.database.input_file import InputFile

logger = logging.getLogger(__name__)


class AlignmentCheckDetails(QFrame):
    def __init__(self):
        super().__init__()
        self.setFrameStyle(QFrame.Shape.Box)

        self._db_id: int | None = None

        self.file_name = QLineEdit()
        self.file_name.setDisabled(True)

        # TODO: Add widgets for viewing the alignment results

        self._set_up_layout()

    def _set_up_layout(self) -> None:
        layout = QGridLayout()
        layout.addWidget(QLabel('File Name: '), 0, 0)
        layout.addWidget(self.file_name, 0, 1)

        self.setLayout(layout)

    def reset(self) -> None:
        self.hide()
        self._db_id = None

    def loaded_id(self) -> int | None:
        return self._db_id

    def load_file(self, db_id: int) -> None:
        self._db_id = db_id

        with Session(DB_ENGINE) as session:
            file = session.get(InputFile, db_id)
            if file is None:
                logger.error(f'No input file found for ID: {db_id}')
                return

            # remove ourselves from view on container items
            if file.container_file:
                self.hide()
                return
            else:
                self.show()

            self.file_name.setText(file.path.name)

            # TODO: Load the alignment results for the file
