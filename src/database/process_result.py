from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, MappedAsDataclass, relationship

from . import OrmBase
from .processed_fields.processed_text_field import ProcessedTextField


class ProcessResult(MappedAsDataclass, OrmBase):
    __tablename__ = "process_result"

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    input_file_id: Mapped[int] = mapped_column(ForeignKey("input_file.id"), init=False)

    # Relationships

    text_field: Mapped[ProcessedTextField] = relationship(default=None, back_populates="process_result")
    # multiline_text_field: Mapped[MultilineTextField] = relationship(default=None, back_populates="form_field")
    # checkbox_field: Mapped[CheckboxField] = relationship(default=None, back_populates="form_field")
    # multi_checkbox_field: Mapped[MultiCheckboxField] = relationship(default=None, back_populates="form_field")

    input_file: Mapped["InputFile"] = relationship(init=False, back_populates="process_results")
