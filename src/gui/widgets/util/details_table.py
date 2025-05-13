from PyQt6.QtCore import QMargins
from PyQt6.QtWidgets import QTableWidget, QWidget, QAbstractItemView

from .table_label import TableLabel


class DetailsTable(QTableWidget):
    def __init__(self, parent: QWidget):
        super().__init__(parent)

        self.setColumnCount(2)
        self.setHorizontalHeaderLabels(['Setting', 'Value'])
        self.horizontalHeader().setStretchLastSection(True)

        # Disable selection
        self.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)

        # Disable row index column
        self.verticalHeader().setVisible(False)

    def resize_table(self) -> None:
        self.resizeRowsToContents()
        self.resizeColumnsToContents()

    def add_row(self, name: str, value: QWidget) -> None:
        next_row_idx = self.rowCount()
        self.setRowCount(next_row_idx + 1)

        self.setCellWidget(next_row_idx, 0, TableLabel(name, QMargins(10, 0, 0, 0)))
        self.setCellWidget(next_row_idx, 1, value)
