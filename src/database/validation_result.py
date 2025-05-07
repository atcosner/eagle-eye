from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, MappedAsDataclass, relationship

from . import OrmBase


class ValidationResult(MappedAsDataclass, OrmBase):
    __tablename__ = "validation_result"

    id: Mapped[int] = mapped_column(init=False, primary_key=True)

    result: Mapped[bool | None]
    explanation: Mapped[str | None]

    # Relationships

    multi_checkbox_field_id: Mapped[int] = mapped_column(
        ForeignKey("processed_multi_checkbox_field.id"),
        init=False,
        nullable=True,
    )
    multi_checkbox_field: Mapped["ProcessedMultiCheckboxField"] = relationship(
        init=False,
        back_populates="validation_result",
    )
