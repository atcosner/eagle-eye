from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, MappedAsDataclass, relationship

from src.util.types import BoxBounds

from .. import OrmBase
from ..util import DbBoxBounds


class MultiCheckboxOption(MappedAsDataclass, OrmBase):
    __tablename__ = "multi_checkbox_option"

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    multi_checkbox_field_id: Mapped[int] = mapped_column(ForeignKey("multi_checkbox_field.id"), init=False)

    name: Mapped[str]
    region: Mapped[BoxBounds] = mapped_column(DbBoxBounds)
    text_region: Mapped[BoxBounds] = mapped_column(DbBoxBounds, nullable=True, default=None)

    # Relationships

    multi_checkbox_field: Mapped["MultiCheckboxField"] = relationship(init=False, back_populates="checkboxes")
