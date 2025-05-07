from pathlib import Path
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, MappedAsDataclass, relationship

from .. import OrmBase
from ..util import DbPath
from ..validation.validation_result import ValidationResult


class ProcessedCheckboxField(MappedAsDataclass, OrmBase):
    __tablename__ = "processed_checkbox_field"

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    processed_field_id: Mapped[int] = mapped_column(ForeignKey("processed_field.id"), init=False)
    checkbox_field_id: Mapped[int] = mapped_column(ForeignKey("checkbox_field.id"), init=False)

    name: Mapped[str]
    roi_path: Mapped[Path] = mapped_column(DbPath)

    checked: Mapped[bool]

    # Relationships

    validation_result: Mapped[ValidationResult] = relationship(back_populates="checkbox_field")

    processed_field: Mapped["ProcessedField"] = relationship(init=False, back_populates="checkbox_field")
    checkbox_field: Mapped["CheckboxField"] = relationship()
