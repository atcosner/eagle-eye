from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, MappedAsDataclass, relationship

from .processed_checkbox_field import ProcessedCheckboxField
from .processed_multi_checkbox_field import ProcessedMultiCheckboxField
from .processed_multiline_text_field import ProcessedMultilineTextField
from .processed_text_field import ProcessedTextField
from .. import OrmBase


class ProcessedField(MappedAsDataclass, OrmBase):
    __tablename__ = "processed_field"

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    processed_region_id: Mapped[int] = mapped_column(ForeignKey("processed_region.id"), init=False)

    processing_error: Mapped[bool]

    # Relationships

    processed_region: Mapped["ProcessedRegion"] = relationship(init=False, back_populates="fields")

    text_field: Mapped[ProcessedTextField] = relationship(default=None, back_populates="processed_field")
    multiline_text_field: Mapped[ProcessedMultilineTextField] = relationship(default=None, back_populates="processed_field")
    checkbox_field: Mapped[ProcessedCheckboxField] = relationship(default=None, back_populates="processed_field")
    multi_checkbox_field: Mapped[ProcessedMultiCheckboxField] = relationship(default=None, back_populates="processed_field")
