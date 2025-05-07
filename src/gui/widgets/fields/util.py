from PyQt6.QtWidgets import QFrame, QWidget, QVBoxLayout, QHBoxLayout


def wrap_in_frame(widget: QWidget, center_horizontal: bool = False) -> QFrame:
    frame = QFrame()
    frame.setLineWidth(2)
    frame.setFrameStyle(QFrame.Shape.Box)

    layout = QVBoxLayout()
    if center_horizontal:
        h_layout = QHBoxLayout()
        h_layout.addStretch()
        h_layout.addWidget(widget)
        h_layout.addStretch()
        layout.addLayout(h_layout)
    else:
        layout.addWidget(widget)
    frame.setLayout(layout)

    return frame
