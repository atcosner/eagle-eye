from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QPixmap


def scale_pixmap(pixmap: QPixmap, size: QSize) -> QPixmap:
    return pixmap.scaled(
        size,
        Qt.AspectRatioMode.KeepAspectRatio,
        Qt.TransformationMode.SmoothTransformation,
    )
