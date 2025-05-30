from PyQt6.QtCore import Qt, pyqtSlot, pyqtSignal
from PyQt6.QtGui import QWheelEvent, QKeyEvent, QCursor
from PyQt6.QtWidgets import QGraphicsView

from src.database.reference_form import ReferenceForm

from .form_scene import FormScene
from .util import SelectionType


class FormFieldCanvas(QGraphicsView):
    fieldSelected = pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self.setMinimumWidth(600)

        self.scene = FormScene()
        self.setScene(self.scene)

        self.scene.fieldSelected.connect(self.fieldSelected)

    def fit_form(self) -> None:
        self.fitInView(self.scene.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)

    def load_reference_form(self, form: ReferenceForm | int | None) -> None:
        self.scene.load_reference_form(form)
        self.fit_form()

    @pyqtSlot(SelectionType, int)
    def handle_tree_selection_change(self, selection: SelectionType, db_id: int) -> None:
        self.scene.handle_tree_selection_change(selection, db_id)

    @pyqtSlot(SelectionType, int)
    def handle_deletion(self, selection: SelectionType, db_id: int) -> None:
        self.scene.handle_deletion(selection, db_id)

    #
    # Qt Event Handlers
    #

    def wheelEvent(self, event: QWheelEvent) -> None:
        if not (event.modifiers() & Qt.KeyboardModifier.ControlModifier):
            super().wheelEvent(event)
        else:
            # Zoom in/out
            current_anchor = self.transformationAnchor()

            self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
            factor = 1.1 if event.angleDelta().y() > 0 else 0.9
            self.scale(factor, factor)

            self.setTransformationAnchor(current_anchor)

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.key() == Qt.Key.Key_Control:
            # TODO: Find a zoom cursor
            self.setCursor(QCursor(Qt.CursorShape.UpArrowCursor))

        super().keyPressEvent(event)

    def keyReleaseEvent(self, event: QKeyEvent) -> None:
        if event.key() == Qt.Key.Key_Control:
            self.setCursor(QCursor(Qt.CursorShape.ArrowCursor))

        super().keyReleaseEvent(event)
