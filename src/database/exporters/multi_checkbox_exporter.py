from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, MappedAsDataclass, relationship

from src.util.export import MultiCbExportType, CapitalizationType

from .. import OrmBase


class MultiCheckboxExporter(MappedAsDataclass, OrmBase):
    __tablename__ = "multi_checkbox_exporter"
    id: Mapped[int] = mapped_column(init=False, primary_key=True)

    no_export: Mapped[bool] = mapped_column(default=False, nullable=False)

    export_field_name: Mapped[str | None] = mapped_column(default=None)
    text_field_name: Mapped[str | None] = mapped_column(default=None)
    capitalization: Mapped[CapitalizationType] = mapped_column(default=CapitalizationType.NONE, nullable=False)

    export_type: Mapped[MultiCbExportType] = mapped_column(default=MultiCbExportType.MULTIPLE_COLUMNS, nullable=False)

    # Relationships

    multi_checkbox_field_id: Mapped[int] = mapped_column(ForeignKey("multi_checkbox_field.id"), init=False, nullable=True)
    multi_checkbox_field: Mapped["MultiCheckboxField"] = relationship(init=False, back_populates="exporter")
