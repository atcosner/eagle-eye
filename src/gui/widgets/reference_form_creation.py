from PyQt6.QtWidgets import QWidget, QHBoxLayout

from src.database.reference_form import ReferenceForm

from .reference_form.field_browser import FieldBrowser
from .reference_form.form_field_canvas import FormFieldCanvas
from .util.line_splitter import LineSplitter


class ReferenceFormCreation(QWidget):
    def __init__(self):
        super().__init__()

        self.field_canvas = FormFieldCanvas()
        self.field_browser = FieldBrowser()

        self._set_up_layout()
        self._connect_signals()

    def _set_up_layout(self) -> None:
        splitter = LineSplitter()
        splitter.addWidget(self.field_canvas)
        splitter.addWidget(self.field_browser)

        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 0)

        layout = QHBoxLayout()
        layout.addWidget(splitter)
        self.setLayout(layout)

    def _connect_signals(self) -> None:
        self.field_browser.treeSelectionChange.connect(self.field_canvas.handle_tree_selection_change)
        self.field_canvas.fieldSelected.connect(self.field_browser.handle_canvas_field_selected)

    def load_reference_form(self, form: ReferenceForm | int | None) -> None:
        self.field_canvas.load_reference_form(form)
        self.field_browser.load_reference_form(form)
