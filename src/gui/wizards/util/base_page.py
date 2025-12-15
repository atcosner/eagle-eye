from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QWizardPage, QWizard

from src.util.resources import RESOURCES_PATH


class BasePage(QWizardPage):
    def __init__(self, title: str):
        super().__init__()
        self.setTitle(title)

        watermark_pixmap = QPixmap(str(RESOURCES_PATH / 'wizard_watermark.png'))
        self.setPixmap(
            QWizard.WizardPixmap.WatermarkPixmap,
            watermark_pixmap.scaled(
                150,
                300,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            ),
        )

        logo_pixmap = QPixmap(str(RESOURCES_PATH / 'white_icon.png'))
        self.setPixmap(
            QWizard.WizardPixmap.LogoPixmap,
            logo_pixmap.scaled(
                64,
                64,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            ),
        )
