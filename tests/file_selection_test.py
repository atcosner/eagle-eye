import sys
from PyQt6.QtCore import Qt, QPoint, QRect, QMimeDatabase, pyqtSlot
from PyQt6.QtGui import QPainter, QImage, QPen, QColor, QMouseEvent, QPaintEvent
from PyQt6.QtWidgets import QApplication, QMainWindow, QListWidget, QFileDialog, QVBoxLayout, QWidget, QHBoxLayout, QListWidgetItem
from PyQt6.QtPdf import QPdfDocument
from PyQt6.QtPdfWidgets import QPdfView
app = QApplication(sys.argv)


class DropList(QListWidget):
    def __init__(self, parent=None):
        super(DropList, self).__init__(parent)
        self.setAcceptDrops(True)

        self.db = QMimeDatabase()

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event):
        md = event.mimeData()
        if md.hasUrls():
            for url in md.urls():
                self.addItem(url.toLocalFile())
                print(self.db.mimeTypeForUrl(url).name())
            event.acceptProposedAction()


class Window(QMainWindow):
    def __init__(self):
        super().__init__()

        self.list = DropList()
        self.document = QPdfDocument(self)
        self.viewer = QPdfView(self)
        self.viewer.setDocument(self.document)

        self.list.currentItemChanged.connect(self.show_pdf)

        widget = QWidget()
        layout = QHBoxLayout()
        layout.addWidget(self.list)
        layout.addWidget(self.viewer)

        widget.setLayout(layout)
        self.setCentralWidget(widget)

    @pyqtSlot(QListWidgetItem, QListWidgetItem)
    def show_pdf(self, current: QListWidgetItem, ):
        res = self.document.load(current.text())
        print(res)


window = Window()
window.show()

app.exec()
