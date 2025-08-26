from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, MappedAsDataclass, relationship

from .form_field import FormField
from .. import OrmBase


class FieldGroup(MappedAsDataclass, OrmBase):
    __tablename__ = "field_group"

    id: Mapped[int] = mapped_column(init=False, primary_key=True)

    name: Mapped[str]

    # Relationships

    form_region_id: Mapped[int] = mapped_column(ForeignKey("form_region.id"), init=False)
    form_region: Mapped["FormRegion"] = relationship(init=False, back_populates="groups")

    fields: Mapped[list[FormField]] = relationship(back_populates="field_group")
