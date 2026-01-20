from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, MappedAsDataclass, relationship

from src.util.types import BoxBounds
from src.util.validation import MultiChoiceValidation

from .circled_option import CircledOption
from .. import OrmBase
from ..exporters.circled_exporter import CircledExporter
from ..util import DbBoxBounds


class CircledField(MappedAsDataclass, OrmBase):
    __tablename__ = "circled_field"

    id: Mapped[int] = mapped_column(init=False, primary_key=True)

    name: Mapped[str]
    visual_region: Mapped[BoxBounds] = mapped_column(DbBoxBounds)
    validator: Mapped[MultiChoiceValidation]

    # Relationships

    options: Mapped[list[CircledOption]] = relationship(back_populates="circled_field")

    exporter: Mapped[CircledExporter] = relationship(default=None, back_populates="circled_field")

    form_field_id: Mapped[int] = mapped_column(ForeignKey("form_field.id"), init=False)
    form_field: Mapped["FormField"] = relationship(init=False, back_populates="circled_field")
