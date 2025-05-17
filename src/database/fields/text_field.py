from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, MappedAsDataclass, relationship

from src.util.types import BoxBounds

from .. import OrmBase
from ..exporters.text_exporter import TextExporter
from ..util import DbBoxBounds, ListDbBoxBounds
from ..validation.text_validator import TextValidator


class TextField(MappedAsDataclass, OrmBase):
    __tablename__ = "text_field"
    id: Mapped[int] = mapped_column(init=False, primary_key=True)

    name: Mapped[str]
    visual_region: Mapped[BoxBounds] = mapped_column(DbBoxBounds)
    text_regions: Mapped[list[BoxBounds]] = mapped_column(ListDbBoxBounds, nullable=True, default=None)

    # Support for text fields that have a default checkbox
    checkbox_region: Mapped[BoxBounds] = mapped_column(DbBoxBounds, nullable=True, default=None)
    checkbox_text: Mapped[str] = mapped_column(nullable=True, default=None)

    allow_copy: Mapped[bool] = mapped_column(default=False)

    # Relationships

    text_exporter: Mapped[TextExporter] = relationship(default=None, back_populates="text_field")
    text_validator: Mapped[TextValidator] = relationship(default=None, back_populates="text_field")

    form_field_id: Mapped[int] = mapped_column(ForeignKey("form_field.id"), init=False)
    form_field: Mapped["FormField"] = relationship(init=False, back_populates="text_field")
