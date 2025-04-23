from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, MappedAsDataclass, relationship

from . import OrmBase
from .fields.form_field import FormField


class FormRegion(MappedAsDataclass, OrmBase):
    __tablename__ = "form_region"

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    reference_form_id: Mapped[int] = mapped_column(ForeignKey("reference_form.id"), init=False)

    local_id: Mapped[int]
    name: Mapped[str]

    # Relationships

    reference_form: Mapped["ReferenceForm"] = relationship(init=False, back_populates="regions")
    fields: Mapped[list[FormField]] = relationship(init=False, back_populates="form_region")
