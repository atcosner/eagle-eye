from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, MappedAsDataclass, relationship

from src.util.export import CapitalizationType

from .. import OrmBase


class CircledExporter(MappedAsDataclass, OrmBase):
    __tablename__ = "circled_exporter"
    id: Mapped[int] = mapped_column(init=False, primary_key=True)

    no_export: Mapped[bool] = mapped_column(default=False, nullable=False)

    export_field_name: Mapped[str | None] = mapped_column(default=None)
    capitalization: Mapped[CapitalizationType] = mapped_column(default=CapitalizationType.LOWER, nullable=False)

    # Relationships

    circled_field_id: Mapped[int] = mapped_column(ForeignKey("circled_field.id"), init=False, nullable=True)
    circled_field: Mapped["CircledField"] = relationship(init=False, back_populates="exporter")
