from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, MappedAsDataclass, relationship

from src.util.types import BoxBounds
from src.util.validation import MultiChoiceValidation

from .multi_checkbox_option import MultiCheckboxOption
from .. import OrmBase
from ..util import DbBoxBounds


class MultiCheckboxField(MappedAsDataclass, OrmBase):
    __tablename__ = "multi_checkbox_field"

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    form_field_id: Mapped[int] = mapped_column(ForeignKey("form_field.id"), init=False)

    name: Mapped[str]
    visual_region: Mapped[BoxBounds] = mapped_column(DbBoxBounds)
    validator: Mapped[MultiChoiceValidation]

    # Relationships

    checkboxes: Mapped[list[MultiCheckboxOption]] = relationship(back_populates="multi_checkbox_field")
    form_field: Mapped["FormField"] = relationship(init=False, back_populates="multi_checkbox_field")
