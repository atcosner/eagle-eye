from PyQt6.QtGui import QColor, QIcon, QPixmap

# Rotating hue by the golden angle (~222.5°) on each step maximizes the perceptual distance
# between successive colors around the color wheel.
_GOLDEN_RATIO = 0.618033988749895


def get_region_color(index: int) -> QColor:
    hue = (index * _GOLDEN_RATIO * 360) % 360
    return QColor.fromHslF(hue / 360.0, 0.75, 0.40)


def get_icon_for_region(index: int) -> QIcon:
    pixmap = QPixmap(64, 64)
    pixmap.fill(get_region_color(index))
    return QIcon(pixmap)
