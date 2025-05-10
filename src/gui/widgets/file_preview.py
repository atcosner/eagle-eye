import logging

from PyQt6.QtCore import Qt, QMimeDatabase, QPoint, QPointF
from PyQt6.QtGui import QPixmap, QMouseEvent, QWheelEvent, QKeyEvent, QEnterEvent, QCursor
from PyQt6.QtPdf import QPdfDocument
from PyQt6.QtPdfWidgets import QPdfView
from PyQt6.QtWidgets import QWidget, QScrollArea, QLabel, QSizePolicy, QVBoxLayout, QPushButton, QHBoxLayout, QScrollBar

from .util.dropdown_button import FitImageButton

from pathlib import Path

logger = logging.getLogger(__name__)


def adjust_scroll_bar_scale(bar: QScrollBar, factor: float) -> None:
    bar.setValue(int(factor * bar.value() + ((factor - 1) * bar.pageStep() / 2)))


class ImageViewer(QScrollArea):
    def __init__(self):
        super().__init__()
        self.last_drag_position: QPoint | None = None
        self.mouse_in_widget = False
        self.control_pressed = False

        self.setMouseTracking(True)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        self.image_label = QLabel()
        self.image_label.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Ignored)
        self.image_label.setScaledContents(True)

        self.setWidget(self.image_label)
        self.update_cursor()

    def load_image(self, file_path: str) -> None:
        self.image_label.setPixmap(QPixmap(file_path))
        self.reset_zoom()

    def reset_zoom(self) -> None:
        # Scale the image so it is fully visible at the current size
        self.image_label.resize(
            # QSize auto-scale while preserving the aspect ratio
            self.image_label.pixmap().size().scaled(
                self.viewport().size(),
                Qt.AspectRatioMode.KeepAspectRatio,
            )
        )

    def fit_to_width(self):
        # TODO: If the image is landscape this won't be correct
        self.image_label.resize(
            # Resize to the viewport but allow us to expand outside the viewport
            self.image_label.pixmap().size().scaled(
                self.viewport().size(),
                Qt.AspectRatioMode.KeepAspectRatioByExpanding,
            )
        )

    def adjust_scale(self, factor: float) -> None:
        logger.info(f'Adjusting scale by: {factor}')
        self.image_label.resize(factor * self.image_label.size())

        adjust_scroll_bar_scale(self.horizontalScrollBar(), factor)
        adjust_scroll_bar_scale(self.verticalScrollBar(), factor)

    def scale_mouse_anchor(self, factor: float, mouse_loc: QPointF) -> None:
        current_scroll = QPoint(self.horizontalScrollBar().value(), self.verticalScrollBar().value())
        delta_to_mouse = mouse_loc - self.widget().pos().toPointF()

        scaled_delta = (delta_to_mouse * factor - delta_to_mouse).toPoint()
        self.image_label.resize(factor * self.image_label.size())

        self.horizontalScrollBar().setValue(current_scroll.x() + scaled_delta.x())
        self.verticalScrollBar().setValue(current_scroll.y() + scaled_delta.y())

    def update_cursor(self) -> None:
        if self.mouse_in_widget and self.control_pressed:
            self.setCursor(QCursor(Qt.CursorShape.UpArrowCursor))
        else:
            self.setCursor(QCursor(Qt.CursorShape.SizeAllCursor))

    #
    # Qt Event Handlers
    #

    def enterEvent(self, event: QEnterEvent) -> None:
        self.mouse_in_widget = True
        self.setFocus()
        super().enterEvent(event)

    def leaveEvent(self, event) -> None:
        self.mouse_in_widget = False
        super().leaveEvent(event)

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if self.mouse_in_widget and event.key() == Qt.Key.Key_Control:
            self.control_pressed = True
            self.update_cursor()

        event.accept()

    def keyReleaseEvent(self, event: QKeyEvent) -> None:
        if event.key() == Qt.Key.Key_Control:
            self.control_pressed = False
            self.update_cursor()

        event.accept()

    def wheelEvent(self, event: QWheelEvent) -> None:
        # Check if the user is holding down Ctrl
        if self.mouse_in_widget and self.control_pressed:
            if event.angleDelta().y() > 0:
                self.scale_mouse_anchor(1.25, event.position())
            else:
                self.scale_mouse_anchor(0.8, event.position())
        else:
            super().wheelEvent(event)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        super().mousePressEvent(event)
        self.last_drag_position = event.pos()

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        super().mouseReleaseEvent(event)
        self.last_drag_position = None

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        super().mouseMoveEvent(event)

        if self.last_drag_position is not None:
            delta = event.pos() - self.last_drag_position
            self.last_drag_position = event.pos()

            self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - delta.x())
            self.verticalScrollBar().setValue(self.verticalScrollBar().value() - delta.y())


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

    def fit_to_width(self):
        self.setZoomMode(QPdfView.ZoomMode.FitToWidth)

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

        self.fit_button = FitImageButton()
        self.fit_button.fitToWindow.connect(self.reset_scale)
        self.fit_button.fitToWidth.connect(self.fit_to_width)

        self.zoom_in_button.pressed.connect(lambda: self.update_scale(1.25))
        self.zoom_out_button.pressed.connect(lambda: self.update_scale(0.8))

        self.pdf_viewer = PdfViewer()
        self.image_viewer = ImageViewer()

        self.image_viewer.setVisible(False)

        zoom_layout = QHBoxLayout()
        zoom_layout.addWidget(self.zoom_in_button)
        zoom_layout.addWidget(self.zoom_out_button)
        zoom_layout.addStretch()
        zoom_layout.addWidget(self.fit_button)

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

    def fit_to_width(self) -> None:
        self.image_viewer.fit_to_width()
        self.pdf_viewer.fit_to_width()

    def update_preview(self, file_path: str | Path) -> None:
        if isinstance(file_path, Path):
            file_path = str(file_path)

        mime_type = self.mime_db.mimeTypeForFile(file_path)

        # Split based on if it is an image or PDF
        # TODO: Qt says I should use .inherit() here?
        if mime_type.name().startswith('image'):
            self.pdf_viewer.setVisible(False)
            self.image_viewer.setVisible(True)

            self.image_viewer.load_image(file_path)
        else:
            # PDF
            self.pdf_viewer.setVisible(True)
            self.image_viewer.setVisible(False)

            self.pdf_viewer.load_document(file_path)
