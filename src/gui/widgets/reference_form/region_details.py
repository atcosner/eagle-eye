from PyQt6.QtWidgets import QWidget, QLabel

from src.database.form_region import FormRegion

from ..util.details_table import DetailsTable


class RegionDetails(DetailsTable):
    def __init__(self, parent: QWidget):
        super().__init__(parent)

        self.region_name = QLabel()
        self.add_row('Name', self.region_name)

        self.region_id = QLabel()
        self.add_row('Local ID', self.region_id)

    def load_region(self, region: FormRegion) -> str:
        self.region_name.setText(region.name)
        self.region_id.setText(str(region.id))

        return region.name
