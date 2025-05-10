from PyQt6.QtWidgets import QWidget

from src.database.form_region import FormRegion


class RegionDetails(QWidget):
    def __init__(self, parent: QWidget):
        super().__init__(parent)

    def load_region(self, region: FormRegion) -> None:
        pass
