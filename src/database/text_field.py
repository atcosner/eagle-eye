from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, MappedAsDataclass, relationship

from src.util.types import BoxBounds

from . import OrmBase
from .util import DbBoxBounds


class TextField(MappedAsDataclass, OrmBase):
    __tablename__ = "text_field"

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    reference_form_id = mapped_column(ForeignKey("reference_form.id"))

    name: Mapped[str]
    visual_region: Mapped[BoxBounds] = mapped_column(DbBoxBounds)

    # Support for text fields that have a default checkbox
    text_region: Mapped[BoxBounds] = mapped_column(DbBoxBounds, nullable=True, default=None)
    checkbox_region: Mapped[BoxBounds] = mapped_column(DbBoxBounds, nullable=True, default=None)
    checkbox_text: Mapped[str] = mapped_column(nullable=True, default=None)

    allow_copy: Mapped[bool] = mapped_column(default=False)

    # Relationships

    reference_form: Mapped["ReferenceForm"] = relationship(init=False, back_populates="text_fields")
