from PyQt6.QtWidgets import QWidget, QLabel, QPushButton, QHBoxLayout

from src.util.types import BoxBounds


class BoundsWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.bounds_label = QLabel()
        self.edit_button = QPushButton('...')

        layout = QHBoxLayout()
        layout.addWidget(self.bounds_label)
        layout.addStretch()
        layout.addWidget(self.edit_button)
        self.setLayout(layout)

    def load_bounds(self, bounds: BoxBounds) -> None:
        self.bounds_label.setText(bounds.to_widget())
