from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, MappedAsDataclass, relationship

from .. import OrmBase


class ValidationResult(MappedAsDataclass, OrmBase):
    __tablename__ = "validation_result"

    id: Mapped[int] = mapped_column(init=False, primary_key=True)

    result: Mapped[bool | None]
    explanation: Mapped[str | None]

    # UNMAPPED MEMBER
    # - A text correction that should not be written to the DB
    correction: str | None = None

    # Relationships

    text_field_id: Mapped[int] = mapped_column(
        ForeignKey("processed_text_field.id"),
        init=False,
        nullable=True,
    )
    text_field: Mapped["ProcessedTextField"] = relationship(
        init=False,
        back_populates="validation_result",
    )

    multiline_text_field_id: Mapped[int] = mapped_column(
        ForeignKey("processed_multiline_text_field.id"),
        init=False,
        nullable=True,
    )
    multiline_text_field: Mapped["ProcessedMultilineTextField"] = relationship(
        init=False,
        back_populates="validation_result",
    )

    multi_checkbox_field_id: Mapped[int] = mapped_column(
        ForeignKey("processed_multi_checkbox_field.id"),
        init=False,
        nullable=True,
    )
    multi_checkbox_field: Mapped["ProcessedMultiCheckboxField"] = relationship(
        init=False,
        back_populates="validation_result",
    )

    checkbox_field_id: Mapped[int] = mapped_column(
        ForeignKey("processed_checkbox_field.id"),
        init=False,
        nullable=True,
    )
    checkbox_field: Mapped["ProcessedCheckboxField"] = relationship(
        init=False,
        back_populates="validation_result",
    )
