import sys
from PyQt6.QtCore import Qt, QPoint, QRect, QMimeDatabase, pyqtSlot, QSize
from PyQt6.QtGui import QPainter, QImage, QPen, QColor, QMouseEvent, QPaintEvent, QPixmap, QIcon
from PyQt6.QtWidgets import QApplication, QMainWindow, QListWidget, QFileDialog, QVBoxLayout, QWidget, QHBoxLayout, \
    QListWidgetItem, QLabel, QSplitter, QScrollArea, QSizePolicy
from PyQt6.QtPdf import QPdfDocument
from PyQt6.QtPdfWidgets import QPdfView
from PyQt6.uic.Compiler.qtproxies import QtCore

from src.gui.widgets.file_drop_list import FileDropList, FileItem
from src.gui.widgets.file_preview import FilePreview

app = QApplication(sys.argv)


class Window(QMainWindow):
    def __init__(self):
        super().__init__()

        self.list = FileDropList()
        self.preview = FilePreview()

        self.list.currentItemChanged.connect(self.update_preview)

        widget = QWidget()
        layout = QHBoxLayout()
        layout.addWidget(self.list)
        layout.addWidget(self.preview)

        widget.setLayout(layout)
        self.setCentralWidget(widget)
        self.resize(800, 500)

    @pyqtSlot(QListWidgetItem, QListWidgetItem)
    def update_preview(self, current: QListWidgetItem, previous: QListWidgetItem):
        self.preview.update_preview(current.path())


window = Window()
window.show()

app.exec()
