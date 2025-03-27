from PyQt6.QtWidgets import QTreeWidget, QTreeWidgetItem


class FileStatusItem(QTreeWidgetItem):
    def __init__(self):
        super().__init__()


class FileStatusList(QTreeWidget):
    def __init__(self):
        super().__init__()
        self.setColumnCount(3)
