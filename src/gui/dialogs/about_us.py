from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QTextEdit, QDialog

from src.util.resources import RESOURCES_PATH

from src.gui.widgets.util.link_label import LinkLabel


class AboutUs(QDialog):
    def __init__(self, parent: QWidget | None):
        super().__init__(parent)
        self.setWindowTitle('About Us')
        self.setMinimumWidth(400)
        self.setWindowModality(Qt.WindowModality.WindowModal)

        self.title_label = QLabel('Eagle Eye')
        self.logo_label = QLabel()
        self.github_label = LinkLabel(
            r'<a href="https://github.com/atcosner/eagle-eye">GitHub Repo</a>'
        )
        self.description = QTextEdit()

        self._initial_setup()
        self._set_up_layout()

    def _initial_setup(self) -> None:
        pixmap = QPixmap(str(RESOURCES_PATH / 'white_icon.png')).scaled(
            80,
            80,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        self.logo_label.setPixmap(pixmap)

        title_font = self.title_label.font()
        title_font.setBold(True)
        title_font.setPointSize(32)
        self.title_label.setFont(title_font)

        self.description.setReadOnly(True)

        with (RESOURCES_PATH / 'about_us.html').open('rt', encoding='utf-8') as f:
            strings = f.readlines()
            self.description.setHtml(''.join(strings))

    def _set_up_layout(self) -> None:
        logo_layout = QHBoxLayout()
        logo_layout.addStretch()
        logo_layout.addWidget(self.logo_label)
        logo_layout.addStretch()

        title_layout = QHBoxLayout()
        title_layout.addStretch()
        title_layout.addWidget(self.title_label)
        title_layout.addStretch()

        github_layout = QHBoxLayout()
        github_layout.addStretch()
        github_layout.addWidget(self.github_label)
        github_layout.addStretch()

        layout = QVBoxLayout()
        layout.addLayout(logo_layout)
        layout.addLayout(title_layout)
        layout.addLayout(github_layout)
        layout.addWidget(self.description)

        self.setLayout(layout)
