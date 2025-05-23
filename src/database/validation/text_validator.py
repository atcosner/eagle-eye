from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, MappedAsDataclass, relationship

from src.util.validation import TextValidatorDatatype

from .text_choice import TextChoice
from .. import OrmBase


class TextValidator(MappedAsDataclass, OrmBase):
    __tablename__ = "text_validator"
    id: Mapped[int] = mapped_column(init=False, primary_key=True)

    datatype: Mapped[TextValidatorDatatype] = mapped_column(default=TextValidatorDatatype.RAW_TEXT)
    text_required: Mapped[bool] = mapped_column(default=True)

    text_regex: Mapped[str | None] = mapped_column(default=None)
    reformat_regex: Mapped[str | None] = mapped_column(default=None)
    error_tooltip: Mapped[str | None] = mapped_column(default=None)
    allow_closest_match_correction: Mapped[bool] = mapped_column(default=False)

    # Relationships

    text_choices: Mapped[list[TextChoice]] = relationship(default_factory=list, back_populates="text_validator")

    text_field_id: Mapped[int] = mapped_column(ForeignKey("text_field.id"), init=False, nullable=True)
    text_field: Mapped["TextField"] = relationship(init=False, back_populates="text_validator")
