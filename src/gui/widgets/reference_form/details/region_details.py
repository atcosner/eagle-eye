from PyQt6.QtWidgets import QWidget

from src.database.form_region import FormRegion

from ...util.details_tree import BaseFieldDetails, TextItem


class RegionDetails(BaseFieldDetails):
    def __init__(self, parent: QWidget, region: FormRegion):
        super().__init__()
        self.setParent(parent)

        self.name = ''
        self.region_id = TextItem(self, 'Local ID')
        self._load_region(region)

    def _load_region(self, region: FormRegion) -> None:
        self.name = region.name
        super()._load(self.name, None)
        self.region_id.load(region.id)

    def get_name(self) -> str:
        return self.name
