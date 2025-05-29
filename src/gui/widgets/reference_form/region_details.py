from PyQt6.QtWidgets import QWidget, QLabel

from src.database.form_region import FormRegion

from ..util.details_tree import DetailsTree, TextItem


class RegionDetails(DetailsTree):
    def __init__(self, parent: QWidget, region: FormRegion):
        super().__init__()
        self.setParent(parent)

        self.name = None
        self.region_name = TextItem(self, 'Name')
        self.region_id = TextItem(self, 'Local ID')
        self._load_region(region)

    def _load_region(self, region: FormRegion) -> None:
        self.name = region.name
        self.region_name.load(region.name)
        self.region_id.load(region.id)

    def get_name(self) -> str:
        return self.name
