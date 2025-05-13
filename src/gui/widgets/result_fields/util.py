from PyQt6.QtWidgets import QFrame, QWidget, QLayout, QVBoxLayout, QHBoxLayout


def wrap_in_frame(
        obj: QWidget | QLayout,
        center_horizontal: bool = False,
) -> QFrame:
    frame = QFrame()
    frame.setLineWidth(2)
    frame.setFrameStyle(QFrame.Shape.Box)

    if isinstance(obj, QWidget):
        layout = QVBoxLayout()
        if center_horizontal:
            h_layout = QHBoxLayout()
            h_layout.addStretch()
            h_layout.addWidget(obj)
            h_layout.addStretch()
            layout.addLayout(h_layout)
        else:
            layout.addWidget(obj)
        frame.setLayout(layout)
    else:
        frame.setLayout(obj)

    return frame
