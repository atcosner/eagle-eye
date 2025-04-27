from pathlib import Path
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, MappedAsDataclass, relationship

from .. import OrmBase
from ..util import DbPath


class ProcessedTextField(MappedAsDataclass, OrmBase):
    __tablename__ = "processed_text_field"

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    processed_field_id: Mapped[int] = mapped_column(ForeignKey("processed_field.id"), init=False)
    text_field_id: Mapped[int] = mapped_column(ForeignKey("text_field.id"), init=False)

    name: Mapped[str]
    roi_path: Mapped[Path] = mapped_column(DbPath)

    text: Mapped[str]  # Text post any user corrections
    ocr_text: Mapped[str]  # Original OCR result
    copied_from_linked: Mapped[bool]
    from_controlled_language: Mapped[bool]

    # Relationships

    processed_field: Mapped["ProcessedField"] = relationship(init=False, back_populates="text_field")
    text_field: Mapped["TextField"] = relationship()
