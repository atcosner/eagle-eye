from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, MappedAsDataclass, relationship

from src.util.types import BoxBounds

from .. import OrmBase
from ..util import DbBoxBounds


class MultilineTextField(MappedAsDataclass, OrmBase):
    __tablename__ = "multiline_text_field"

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    form_field_id: Mapped[int] = mapped_column(ForeignKey("form_field.id"), init=False)

    name: Mapped[str]
    visual_region: Mapped[BoxBounds] = mapped_column(DbBoxBounds)
    line_regions: Mapped[list[BoxBounds]] = mapped_column(DbBoxBounds)

    # Relationships

    form_field: Mapped["FormField"] = relationship(init=False, back_populates="multiline_text_field")
