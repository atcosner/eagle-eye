from PyQt6.QtCore import Qt, pyqtSignal, pyqtSlot
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QHBoxLayout

from src.database.reference_form import ReferenceForm

from .form_region_tree import FormRegionTree
from .selection_details import SelectionDetails
from .util import SelectionType
from ..util.line_splitter import LineSplitter


class FieldBrowser(LineSplitter):
    deleteSelection = pyqtSignal(SelectionType, int)
    treeSelectionChange = pyqtSignal(SelectionType, int)

    def __init__(self):
        super().__init__()
        self.setOrientation(Qt.Orientation.Vertical)
        self.setMinimumWidth(300)

        self.region_tree = FormRegionTree()
        self.selection_details = SelectionDetails()

        self.add_button = QPushButton('Add')
        self.delete_button = QPushButton('Delete')

        self._connect_signals()
        self._set_up_layout()

    def _connect_signals(self) -> None:
        self.region_tree.updateDetails.connect(self.selection_details.load_details)
        self.region_tree.updateDetails.connect(self.treeSelectionChange)

        self.delete_button.pressed.connect(self.handle_delete_pressed)

    def _set_up_layout(self) -> None:
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.addWidget(self.add_button)
        button_layout.addStretch()
        button_layout.addWidget(self.delete_button)

        dummy_layout = QVBoxLayout()
        dummy_layout.addLayout(button_layout)
        dummy_layout.addWidget(self.region_tree)

        dummy_widget = QWidget()
        dummy_widget.setContentsMargins(0, 0, 0, 0)
        dummy_widget.setLayout(dummy_layout)

        self.addWidget(dummy_widget)
        self.addWidget(self.selection_details)

    def load_reference_form(self, form: ReferenceForm | int | None) -> None:
        self.region_tree.load_reference_form(form)
        self.selection_details.load_reference_form(form)

    @pyqtSlot(int)
    def handle_canvas_field_selected(self, db_id: int) -> None:
        self.region_tree.update_selection(SelectionType.FIELD, db_id)

    @pyqtSlot()
    def handle_delete_pressed(self) -> None:
        result = self.region_tree.delete_selected_item()
        if result is None:
            return

        self.deleteSelection.emit(result[0], result[1])
