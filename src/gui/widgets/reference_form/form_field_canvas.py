from PyQt6.QtCore import Qt, pyqtSlot, pyqtSignal, QRect
from PyQt6.QtGui import QWheelEvent, QKeyEvent, QCursor
from PyQt6.QtWidgets import QGraphicsView

from src.database.reference_form import ReferenceForm

from .form_scene import FormScene
from .util import SelectionType


class FormFieldCanvas(QGraphicsView):
    fieldSelected = pyqtSignal(int)
    fieldPositionUpdate = pyqtSignal(int, QRect)

    def __init__(self):
        super().__init__()
        self.setMinimumWidth(600)

        self._scene = FormScene()
        self.setScene(self._scene)

        self._scene.fieldSelected.connect(self.fieldSelected)
        self._scene.fieldPositionUpdate.connect(self.fieldPositionUpdate)
    
    def set_edit_mode(self, allow_edits: bool) -> None:
        self._scene.set_edit_mode(allow_edits)

    def fit_form(self) -> None:
        self.fitInView(self._scene.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)

    def load_reference_form(self, form: ReferenceForm | int | None) -> None:
        self._scene.load_reference_form(form)
        self.fit_form()

    @pyqtSlot(SelectionType, int)
    def handle_tree_selection_change(self, selection: SelectionType, db_id: int) -> None:
        self._scene.handle_tree_selection_change(selection, db_id)

    @pyqtSlot(SelectionType, int)
    def handle_deletion(self, selection: SelectionType, db_id: int) -> None:
        self._scene.handle_deletion(selection, db_id)

    #
    # Qt Event Handlers
    #

    def wheelEvent(self, event: QWheelEvent | None) -> None:
        if event is None or not (event.modifiers() & Qt.KeyboardModifier.ControlModifier):
            super().wheelEvent(event)
        else:
            # Zoom in/out
            current_anchor = self.transformationAnchor()

            self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
            factor = 1.1 if event.angleDelta().y() > 0 else 0.9
            self.scale(factor, factor)

            self.setTransformationAnchor(current_anchor)

    def keyPressEvent(self, event: QKeyEvent | None) -> None:
        if event and event.key() == Qt.Key.Key_Control:
            # TODO: Find a zoom cursor
            self.setCursor(QCursor(Qt.CursorShape.UpArrowCursor))

        super().keyPressEvent(event)

    def keyReleaseEvent(self, event: QKeyEvent | None) -> None:
        if event and event.key() == Qt.Key.Key_Control:
            self.setCursor(QCursor(Qt.CursorShape.ArrowCursor))

        super().keyReleaseEvent(event)
