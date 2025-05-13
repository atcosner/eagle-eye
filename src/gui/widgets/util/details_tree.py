from PyQt6.QtWidgets import QWidget, QTreeWidget


class DetailsTree(QTreeWidget):
    def __init__(self):
        super().__init__()

        self.setColumnCount(2)
        self.setHeaderLabels(['Setting', 'Value'])
