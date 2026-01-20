from pathlib import Path
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, MappedAsDataclass, relationship, attribute_keyed_dict

from .processed_circled_option import ProcessedCircledOption
from .. import OrmBase
from ..util import DbPath
from ..validation.validation_result import ValidationResult


class ProcessedCircledField(MappedAsDataclass, OrmBase):
    __tablename__ = "processed_circled_field"

    id: Mapped[int] = mapped_column(init=False, primary_key=True)

    name: Mapped[str]
    roi_path: Mapped[Path] = mapped_column(DbPath)

    # Relationships

    validation_result: Mapped[ValidationResult] = relationship(back_populates="circled_field")

    processed_field_id: Mapped[int] = mapped_column(ForeignKey("processed_field.id"), init=False)
    processed_field: Mapped["ProcessedField"] = relationship(init=False, back_populates="circled_field")

    circled_field_id: Mapped[int] = mapped_column(ForeignKey("circled_field.id"), init=False)
    circled_field: Mapped["CircledField"] = relationship()

    options: Mapped[dict[str, ProcessedCircledOption]] = relationship(
        collection_class=attribute_keyed_dict("name"),
        back_populates="processed_circled_field",
    )
