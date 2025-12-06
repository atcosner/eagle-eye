from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, MappedAsDataclass, relationship

from . import OrmBase
from .fields.field_group import FieldGroup


class FormRegion(MappedAsDataclass, OrmBase):
    __tablename__ = "form_region"

    id: Mapped[int] = mapped_column(init=False, primary_key=True)

    local_id: Mapped[int]
    name: Mapped[str]

    # Relationships

    reference_form_id: Mapped[int] = mapped_column(ForeignKey("reference_form.id"), init=False)
    reference_form: Mapped["ReferenceForm"] = relationship(init=False, back_populates="regions")

    groups: Mapped[list[FieldGroup]] = relationship(init=False, back_populates="form_region")
