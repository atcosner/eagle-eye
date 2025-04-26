from PyQt6.QtWidgets import QFrame, QWidget, QVBoxLayout


def wrap_in_frame(widget: QWidget) -> QFrame:
    frame = QFrame()
    frame.setLineWidth(2)
    frame.setFrameStyle(QFrame.Shape.Box)

    layout = QVBoxLayout()
    layout.addWidget(widget)
    frame.setLayout(layout)

    return frame
