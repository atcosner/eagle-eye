import sys
from PyQt6.QtCore import Qt, QPoint, QRect
from PyQt6.QtGui import QPainter, QImage, QPen, QColor, QMouseEvent, QPaintEvent
from PyQt6.QtWidgets import QApplication, QWidget

class PaintDemo(QWidget):
    def __init__(self):
        super().__init__()
        self.image = QImage(500, 500, QImage.Format.Format_RGB32)
        self.finalized_rects = []
        self.start_point = None

        self.clear()

    def clear(self) -> None:
        self.image.fill(QColor('white'))
        if self.finalized_rects:
            for rect in self.finalized_rects:
                painter = QPainter(self.image)
                painter.setPen(QPen(QColor('red'), 2.0))
                painter.drawRect(rect)

        self.update()

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self.start_point = event.position().toPoint()
            print(self.start_point)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if self.start_point is not None:
            self.draw(event.position().toPoint())

    def mouseReleaseEvent(self, event: QMouseEvent):
        if self.start_point is not None:
            self.finalized_rects.append(
                QRect(self.start_point, event.position().toPoint())
            )

    def paintEvent(self, event: QPaintEvent) -> None:
        painter = QPainter(self)
        painter.drawImage(event.rect(), self.image, event.rect())

    def draw(self, end_point: QPoint) -> None:
        self.clear()

        painter = QPainter(self.image)
        painter.setPen(QPen(QColor('red'), 2.0))
        painter.drawRect(QRect(self.start_point, end_point))
        self.update()


app = QApplication(sys.argv)

window = PaintDemo()
window.show()

app.exec()
