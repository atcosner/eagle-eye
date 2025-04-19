from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, MappedAsDataclass, relationship

from .checkbox_field import CheckboxField
from .multi_checkbox_field import MultiCheckboxField
from .multiline_text_field import MultilineTextField
from .text_field import TextField
from .. import OrmBase


class FormField(MappedAsDataclass, OrmBase):
    __tablename__ = "form_field"

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    page_region_id: Mapped[int] = mapped_column(ForeignKey("page_region.id"), init=False)

    # Relationships

    text_field: Mapped[TextField] = relationship(default=None, back_populates="form_field")
    multiline_text_field: Mapped[MultilineTextField] = relationship(default=None, back_populates="form_field")
    checkbox_field: Mapped[CheckboxField] = relationship(default=None, back_populates="form_field")
    multi_checkbox_field: Mapped[MultiCheckboxField] = relationship(default=None, back_populates="form_field")

    page_region: Mapped["PageRegion"] = relationship(init=False, back_populates="fields")
