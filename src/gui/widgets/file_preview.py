from PyQt6.QtCore import QMimeDatabase
from PyQt6.QtGui import QPixmap
from PyQt6.QtPdf import QPdfDocument
from PyQt6.QtPdfWidgets import QPdfView
from PyQt6.QtWidgets import QWidget, QScrollArea, QLabel, QSizePolicy, QVBoxLayout, QPushButton


class ImageViewer(QScrollArea):
    def __init__(self):
        super().__init__()

        self.pixmap = QPixmap()
        self.image = QLabel()
        self.image.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Ignored)
        self.image.setScaledContents(True)

        self.setWidget(self.image)
        self.setWidgetResizable(True)

    def load_image(self, file_path: str) -> None:
        self.pixmap.load(file_path)
        self.image.setPixmap(self.pixmap)


class PdfViewer(QPdfView):
    def __init__(self):
        super().__init__(None)

        self.document = QPdfDocument(None)

        self.setDocument(self.document)
        self.setZoomMode(QPdfView.ZoomMode.FitInView)
        self.setPageMode(QPdfView.PageMode.MultiPage)

    def load_document(self, file_path: str) -> None:
        self.document.load(file_path)


class FilePreview(QWidget):
    def __init__(self):
        super().__init__()
        self.mime_db = QMimeDatabase()

        # self.zoom_up_button = QPushButton()
        # self.zoom_down_button = QPushButton()

        self.pdf_viewer = PdfViewer()
        self.image_viewer = ImageViewer()

        self.image_viewer.setVisible(False)

        layout = QVBoxLayout()
        layout.addWidget(self.pdf_viewer)
        layout.addWidget(self.image_viewer)
        self.setLayout(layout)

    def update_preview(self, file_path: str) -> None:
        mime_type = self.mime_db.mimeTypeForFile(file_path)

        # Split based on if it is an image or PDF
        # TODO: Qt says I should use .inherit() here
        if mime_type.name().startswith('image'):
            self.pdf_viewer.setVisible(False)
            self.image_viewer.setVisible(True)

            self.image_viewer.load_image(file_path)
        else:
            # PDF
            self.pdf_viewer.setVisible(True)
            self.image_viewer.setVisible(False)

            self.pdf_viewer.load_document(file_path)
