from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QListWidget, QListWidgetItem


class LogViewer(QListWidget):
    def __init__(self) -> None:
        super().__init__(None)

        # use a monospace font
        # TODO: this won't work on Mac or Linux
        self.setFont(QFont('Courier New'))

    def add_line(self, line: str) -> None:
        self.addItem(QListWidgetItem(line))

    def add_lines(self, lines: list[str] | str) -> None:
        if isinstance(lines, str):
            lines = lines.splitlines()

        for line in lines:
            self.add_line(line)
