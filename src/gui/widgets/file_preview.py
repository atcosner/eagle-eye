from PyQt6.QtCore import Qt, QMimeDatabase
from PyQt6.QtGui import QPixmap
from PyQt6.QtPdf import QPdfDocument
from PyQt6.QtPdfWidgets import QPdfView
from PyQt6.QtWidgets import QWidget, QScrollArea, QLabel, QSizePolicy, QVBoxLayout, QPushButton, QHBoxLayout, QScrollBar

from pathlib import Path


def adjust_scroll_bar_scale(bar: QScrollBar, factor: float) -> None:
    bar.setValue(int(factor * bar.value() + ((factor - 1) * bar.pageStep() / 2)))


class ImageViewer(QScrollArea):
    def __init__(self):
        super().__init__()

        self.image_label = QLabel()
        self.image_label.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Ignored)
        self.image_label.setScaledContents(True)

        self.scale_factor = 1.0

        self.setWidget(self.image_label)

    def load_image(self, file_path: str) -> None:
        self.image_label.setPixmap(QPixmap(file_path))
        self.reset_zoom()

    def reset_zoom(self) -> None:
        self.scale_factor = 1.0

        # Scale the image so it is fully visible at the current size
        self.image_label.resize(
            # QSize auto-scale while preserving the aspect ratio
            self.image_label.pixmap().size().scaled(self.size(), Qt.AspectRatioMode.KeepAspectRatio)
        )

    def adjust_scale(self, factor: float) -> None:
        self.scale_factor *= factor
        self.image_label.resize(self.scale_factor * self.image_label.size())

        adjust_scroll_bar_scale(self.horizontalScrollBar(), factor)
        adjust_scroll_bar_scale(self.verticalScrollBar(), factor)


class PdfViewer(QPdfView):
    def __init__(self):
        super().__init__(None)

        self.document = QPdfDocument(None)

        self.scale_factor: float | None = None

        self.setDocument(self.document)
        self.setZoomMode(QPdfView.ZoomMode.FitInView)
        self.setPageMode(QPdfView.PageMode.MultiPage)

    def load_document(self, file_path: str) -> None:
        self.document.load(file_path)
        self.reset_zoom()

    def reset_zoom(self) -> None:
        self.scale_factor = None
        self.setZoomMode(QPdfView.ZoomMode.FitInView)

    def adjust_scale(self, factor: float) -> None:
        if self.scale_factor is None:
            # Initial zoom
            self.scale_factor = 1.0
            self.setZoomMode(QPdfView.ZoomMode.Custom)

        self.scale_factor *= factor
        self.setZoomFactor(self.scale_factor)


class FilePreview(QWidget):
    def __init__(self):
        super().__init__()
        self.mime_db = QMimeDatabase()

        self.zoom_in_button = QPushButton('+')
        self.zoom_out_button = QPushButton('-')
        self.zoom_reset_button = QPushButton('Reset')
        self.zoom_in_button.pressed.connect(lambda: self.update_scale(1.25))
        self.zoom_out_button.pressed.connect(lambda: self.update_scale(0.8))
        self.zoom_reset_button.pressed.connect(self.reset_scale)

        self.pdf_viewer = PdfViewer()
        self.image_viewer = ImageViewer()

        self.image_viewer.setVisible(False)

        zoom_layout = QHBoxLayout()
        zoom_layout.addWidget(self.zoom_in_button)
        zoom_layout.addWidget(self.zoom_out_button)
        zoom_layout.addWidget(self.zoom_reset_button)
        zoom_layout.addStretch()

        layout = QVBoxLayout()
        layout.addLayout(zoom_layout)
        layout.addWidget(self.pdf_viewer)
        layout.addWidget(self.image_viewer)
        self.setLayout(layout)

    def update_scale(self, factor: float) -> None:
        self.image_viewer.adjust_scale(factor)
        self.pdf_viewer.adjust_scale(factor)

    def reset_scale(self) -> None:
        self.image_viewer.reset_zoom()
        self.pdf_viewer.reset_zoom()

    def update_preview(self, file_path: str | Path) -> None:
        if isinstance(file_path, Path):
            file_path = str(file_path)

        mime_type = self.mime_db.mimeTypeForFile(file_path)

        # Split based on if it is an image or PDF
        # TODO: Qt says I should use .inherit() here?d
        if mime_type.name().startswith('image'):
            self.pdf_viewer.setVisible(False)
            self.image_viewer.setVisible(True)

            self.image_viewer.load_image(file_path)
        else:
            # PDF
            self.pdf_viewer.setVisible(True)
            self.image_viewer.setVisible(False)

            self.pdf_viewer.load_document(file_path)
