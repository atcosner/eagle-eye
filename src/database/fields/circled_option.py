from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, MappedAsDataclass, relationship

from src.util.types import BoxBounds

from .. import OrmBase
from ..util import DbBoxBounds


class CircledOption(MappedAsDataclass, OrmBase):
    __tablename__ = "circled_option"

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    circled_field_id: Mapped[int] = mapped_column(ForeignKey("circled_field.id"), init=False)

    name: Mapped[str]
    region: Mapped[BoxBounds] = mapped_column(DbBoxBounds)
    # text_region: Mapped[BoxBounds] = mapped_column(DbBoxBounds, nullable=True, default=None)

    # Relationships

    circled_field: Mapped["CircledField"] = relationship(init=False, back_populates="options")
