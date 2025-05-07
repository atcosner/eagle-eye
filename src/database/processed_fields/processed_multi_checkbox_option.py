from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, MappedAsDataclass, relationship

from src.util.types import BoxBounds
from .processed_text_field import ProcessedTextField

from .. import OrmBase
from ..util import DbBoxBounds


class ProcessedMultiCheckboxOption(MappedAsDataclass, OrmBase):
    __tablename__ = "processed_multi_checkbox_option"

    id: Mapped[int] = mapped_column(init=False, primary_key=True)

    name: Mapped[str]
    checked: Mapped[bool]

    text: Mapped[str] = mapped_column(nullable=True)
    ocr_text: Mapped[str] = mapped_column(nullable=True)

    # Relationships
    multi_checkbox_option_id: Mapped[int] = mapped_column(ForeignKey("multi_checkbox_option.id"), init=False)
    multi_checkbox_option: Mapped["MultiCheckboxOption"] = relationship()

    processed_multi_checkbox_field_id: Mapped[int] = mapped_column(ForeignKey("processed_multi_checkbox_field.id"), init=False)
    processed_multi_checkbox_field: Mapped["ProcessedMultiCheckboxField"] = relationship(init=False, back_populates="checkboxes")
