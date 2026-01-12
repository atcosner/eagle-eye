from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, MappedAsDataclass, relationship

from src.util.export import CapitalizationType, ExportType

from .. import OrmBase


class TextExporter(MappedAsDataclass, OrmBase):
    __tablename__ = "text_exporter"
    id: Mapped[int] = mapped_column(init=False, primary_key=True)

    no_export: Mapped[bool] = mapped_column(default=False, nullable=False)

    export_field_name: Mapped[str | None] = mapped_column(default=None)
    prefix: Mapped[str | None] = mapped_column(default=None)
    suffix: Mapped[str | None] = mapped_column(default=None)
    strip_value: Mapped[bool] = mapped_column(default=True, nullable=False)
    capitalization: Mapped[CapitalizationType] = mapped_column(default=CapitalizationType.NONE, nullable=False)

    export_type: Mapped[ExportType] = mapped_column(default=ExportType.RAW, nullable=False)
    export_group: Mapped[str | None] = mapped_column(default=None)
    element_seperator: Mapped[str] = mapped_column(default=',')

    validator_group_index: Mapped[int | None] = mapped_column(default=None)

    # Relationships

    text_field_id: Mapped[int] = mapped_column(ForeignKey("text_field.id"), init=False, nullable=True)
    text_field: Mapped["TextField"] = relationship(init=False, back_populates="exporters")
