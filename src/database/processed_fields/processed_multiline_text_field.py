from pathlib import Path
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, MappedAsDataclass, relationship

from .. import OrmBase
from ..util import DbPath


class ProcessedMultilineTextField(MappedAsDataclass, OrmBase):
    __tablename__ = "processed_multiline_text_field"

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    processed_field_id: Mapped[int] = mapped_column(ForeignKey("processed_field.id"), init=False)
    multiline_text_field_id: Mapped[int] = mapped_column(ForeignKey("multiline_text_field.id"), init=False)

    name: Mapped[str]
    roi_path: Mapped[Path] = mapped_column(DbPath)

    text: Mapped[str]  # Text post any user corrections
    ocr_result: Mapped[str]  # Original OCR result

    # Relationships

    processed_field: Mapped["ProcessedField"] = relationship(init=False, back_populates="multiline_text_field")
    multiline_text_field: Mapped["MultilineTextField"] = relationship()
