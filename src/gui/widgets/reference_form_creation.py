from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QSplitter

from src.database.reference_form import ReferenceForm

from .reference_form.form_region_tree import FormRegionTree
from .reference_form.selection_details import SelectionDetails


class ReferenceFormCreation(QWidget):
    def __init__(self):
        super().__init__()

        self.region_tree = FormRegionTree()
        self.selection_details = SelectionDetails()

        self._set_up_layout()
        self._connect_signals()

    def _set_up_layout(self) -> None:
        splitter = QSplitter()
        splitter.setOrientation(Qt.Orientation.Vertical)
        splitter.addWidget(self.region_tree)
        splitter.addWidget(self.selection_details)

        layout = QHBoxLayout()
        layout.addWidget(splitter)
        self.setLayout(layout)

    def _connect_signals(self) -> None:
        self.region_tree.updateDetails.connect(self.selection_details.load_details)

    def load_reference_form(self, form: ReferenceForm | int | None) -> None:
        self.region_tree.load_reference_form(form)
