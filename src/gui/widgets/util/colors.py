from PyQt6.QtGui import QColor, QIcon, QPixmap

REGION_COLORS = [
    QColor('red'),
    QColor('green'),
    QColor('blue'),
    QColor('yellow'),
    QColor('magenta'),
    QColor('cyan'),
    QColor('gray'),
    QColor('brown'),
    QColor('pink'),
]


def get_icon_for_region(index: int) -> QIcon:
    pixmap = QPixmap(64, 64)
    pixmap.fill(REGION_COLORS[index])
    return QIcon(pixmap)
