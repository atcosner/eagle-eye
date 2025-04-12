import sys
from PyQt6.QtCore import Qt, QPoint, QRect
from PyQt6.QtGui import QPainter, QImage, QPen, QColor, QMouseEvent, QPaintEvent
from PyQt6.QtWidgets import QApplication, QWidget, QGraphicsScene, QGraphicsView, QGraphicsRectItem, QGraphicsItem

app = QApplication(sys.argv)

parent = QGraphicsRectItem(10, 10, 100, 100)
parent.setPen(QPen(QColor('white'), 1))
parent.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
parent.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)

child = QGraphicsRectItem(0, 0, 10, 10, parent=parent)
child.setPen(QPen(QColor('red'), 1))
child.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
child.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
child.setPos(-10, -10)

scene = QGraphicsScene()
scene.addItem(parent)

view = QGraphicsView(scene)
view.show()

app.exec()