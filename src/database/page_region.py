from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, MappedAsDataclass, relationship

from . import OrmBase
from .fields.form_fields import FormField


class PageRegion(MappedAsDataclass, OrmBase):
    __tablename__ = "page_region"

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    reference_form_id: Mapped[int] = mapped_column(ForeignKey("reference_form.id"), init=False)

    name: Mapped[str]

    # Relationships

    reference_form: Mapped["ReferenceForm"] = relationship(init=False, back_populates="regions")
    fields: Mapped[list[FormField]] = relationship(init=False, back_populates="page_region")
