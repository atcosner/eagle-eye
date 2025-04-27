from PyQt6.QtWidgets import QFileDialog, QWidget


class InputFileDialog(QFileDialog):
    def __init__(self, parent: QWidget):
        super().__init__(parent, 'Please select the files')

        self.setFileMode(QFileDialog.FileMode.ExistingFiles)
        self.setViewMode(QFileDialog.ViewMode.Detail)
        self.setNameFilter('Images & PDFs (*.png *.xpm *.jpg *.jpeg *.pdf)')
