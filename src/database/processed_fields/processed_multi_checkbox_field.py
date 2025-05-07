from pathlib import Path
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, MappedAsDataclass, relationship, attribute_keyed_dict

from .processed_multi_checkbox_option import ProcessedMultiCheckboxOption
from .. import OrmBase
from ..validation_result import ValidationResult
from ..util import DbPath


class ProcessedMultiCheckboxField(MappedAsDataclass, OrmBase):
    __tablename__ = "processed_multi_checkbox_field"

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    processed_field_id: Mapped[int] = mapped_column(ForeignKey("processed_field.id"), init=False)
    multi_checkbox_field_id: Mapped[int] = mapped_column(ForeignKey("multi_checkbox_field.id"), init=False)

    name: Mapped[str]
    roi_path: Mapped[Path] = mapped_column(DbPath)

    # Relationships

    validation_result: Mapped[ValidationResult] = relationship(back_populates="multi_checkbox_field")

    processed_field: Mapped["ProcessedField"] = relationship(init=False, back_populates="multi_checkbox_field")
    multi_checkbox_field: Mapped["MultiCheckboxField"] = relationship()
    checkboxes: Mapped[dict[str, ProcessedMultiCheckboxOption]] = relationship(
        collection_class=attribute_keyed_dict("name"),
        back_populates="processed_multi_checkbox_field",
    )
