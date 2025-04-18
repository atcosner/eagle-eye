from pathlib import Path
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, MappedAsDataclass, relationship

from .. import OrmBase
from ..util import DbPath


class ProcessedTextField(MappedAsDataclass, OrmBase):
    __tablename__ = "processed_text_field"

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    process_result_id: Mapped[int] = mapped_column(ForeignKey("process_result.id"), init=False)
    text_field_id: Mapped[int] = mapped_column(ForeignKey("text_field.id"), init=False)

    name: Mapped[str]
    page_region: Mapped[str]
    roi_path: Mapped[Path] = mapped_column(DbPath)

    ocr_result: Mapped[str]
    allow_linking: Mapped[bool]
    copied_from_linked: Mapped[bool]
    from_controlled_language: Mapped[bool]

    # Relationships

    process_result: Mapped["ProcessResult"] = relationship(init=False, back_populates="text_field")
    text_field: Mapped["TextField"] = relationship(init=False)
