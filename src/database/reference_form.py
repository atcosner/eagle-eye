from sqlalchemy.orm import Mapped, mapped_column, MappedAsDataclass, relationship

from . import OrmBase
from .text_field import TextField


class ReferenceForm(MappedAsDataclass, OrmBase):
    __tablename__ = "reference_form"

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    name: Mapped[str]
    template_path: Mapped[str]  # Path

    reference_mark_count: Mapped[int]
    whole_page_form: Mapped[bool]

    # Relationships

    text_fields: Mapped[list[TextField]] = relationship(init=False, back_populates="reference_form")
