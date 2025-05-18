from PyQt6.QtCore import Qt, pyqtSignal, pyqtSlot

from src.database.reference_form import ReferenceForm

from .form_region_tree import FormRegionTree
from .selection_details import SelectionDetails
from .util import SelectionType
from ..util.line_splitter import LineSplitter


class FieldBrowser(LineSplitter):
    treeSelectionChange = pyqtSignal(SelectionType, int)

    def __init__(self):
        super().__init__()
        self.setOrientation(Qt.Orientation.Vertical)
        self.setMinimumWidth(300)

        self.region_tree = FormRegionTree()
        self.selection_details = SelectionDetails()

        self.addWidget(self.region_tree)
        self.addWidget(self.selection_details)

        self._connect_signals()

    def _connect_signals(self) -> None:
        self.region_tree.updateDetails.connect(self.selection_details.load_details)
        self.region_tree.updateDetails.connect(self.treeSelectionChange)

    def load_reference_form(self, form: ReferenceForm | int | None) -> None:
        self.region_tree.load_reference_form(form)

    @pyqtSlot(int)
    def handle_canvas_field_selected(self, db_id: int) -> None:
        self.region_tree.update_selection(SelectionType.FIELD, db_id)

