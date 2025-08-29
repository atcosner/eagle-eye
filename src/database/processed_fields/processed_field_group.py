from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, MappedAsDataclass, relationship

from .. import OrmBase
from ..processed_fields.processed_field import ProcessedField


class ProcessedFieldGroup(MappedAsDataclass, OrmBase):
    __tablename__ = "processed_field_group"

    id: Mapped[int] = mapped_column(init=False, primary_key=True)

    name: Mapped[str]

    # Relationships

    processed_region_id: Mapped[int] = mapped_column(ForeignKey("processed_region.id"), init=False)
    processed_region: Mapped["ProcessedRegion"] = relationship(init=False, back_populates="groups")

    fields: Mapped[list[ProcessedField]] = relationship(init=False, back_populates="processed_group")
