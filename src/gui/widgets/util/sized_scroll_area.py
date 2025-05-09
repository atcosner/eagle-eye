from PyQt6.QtCore import QSize
from PyQt6.QtWidgets import QScrollArea, QWidget, QSizePolicy


class SizedScrollArea(QScrollArea):
    def __init__(self, widget: QWidget):
        super().__init__()
        self.setWidgetResizable(True)
        self.setWidget(widget)

        size_policy = QSizePolicy()
        size_policy.setHorizontalPolicy(QSizePolicy.Policy.MinimumExpanding)
        self.setSizePolicy(size_policy)

    def sizeHint(self) -> QSize:
        # Indicate we would like to display
        widget_size_hint = self.widget().size()
        widget_size_hint.setWidth(int(widget_size_hint.width() * 0.8))
        return widget_size_hint
