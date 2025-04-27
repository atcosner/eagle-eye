from PyQt6.QtCore import QSize, QRect, QPoint
from PyQt6.QtGui import QPaintEvent
from PyQt6.QtWidgets import QTabWidget, QTabBar, QStylePainter, QStyleOptionTab, QStyle


class VerticalTabBar(QTabBar):
    def __init__(self) -> None:
        super().__init__()

    def tabSizeHint(self, index: int) -> QSize:
        size = super().tabSizeHint(index)
        size.transpose()
        return size

    def paintEvent(self, event: QPaintEvent | None) -> None:
        painter = QStylePainter(self)
        option = QStyleOptionTab()

        for index in range(self.count()):
            self.initStyleOption(option, index)
            painter.drawControl(QStyle.ControlElement.CE_TabBarTabShape, option)
            painter.save()

            size = option.rect.size()
            size.transpose()
            rect = QRect(QPoint(), size)
            rect.moveCenter(option.rect.center())
            option.rect = rect

            center = self.tabRect(index).center()
            painter.translate(center)
            painter.rotate(90)
            painter.translate(-center)
            painter.drawControl(QStyle.ControlElement.CE_TabBarTabLabel, option)
            painter.restore()


class VerticalTabs(QTabWidget):
    def __init__(self, left_side: bool = True):
        super().__init__()
        self.setTabBar(VerticalTabBar())
        self.setTabPosition(QTabWidget.TabPosition.West if left_side else QTabWidget.TabPosition.East)
