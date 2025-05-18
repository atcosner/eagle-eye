from sqlalchemy.orm import Session

from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QGraphicsScene, QGraphicsPixmapItem

from src.database import DB_ENGINE
from src.database.reference_form import ReferenceForm


class FormScene(QGraphicsScene):
    def __init__(self):
        super().__init__()
        self._form_db_id: int | None = None

        self.reference_pixmap: QGraphicsPixmapItem | None = None

    def load_reference_form(self, form: ReferenceForm | int | None) -> None:
        self._form_db_id = None
        if form is None:
            return

        with Session(DB_ENGINE) as session:
            form = session.get(ReferenceForm, form) if isinstance(form, int) else form
            self._form_db_id = form.id

            self.reference_pixmap = self.addPixmap(QPixmap(str(form.path)))
