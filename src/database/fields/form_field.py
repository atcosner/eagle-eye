from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, MappedAsDataclass, relationship

from .checkbox_field import CheckboxField
from .multi_checkbox_field import MultiCheckboxField
from .text_field import TextField
from .. import OrmBase


class FormField(MappedAsDataclass, OrmBase):
    __tablename__ = "form_field"

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    form_region_id: Mapped[int] = mapped_column(ForeignKey("form_region.id"), init=False)

    identifier: Mapped[bool] = mapped_column(default=False)
    identifier_regex: Mapped[str] = mapped_column(nullable=True, default=None)

    # Relationships

    text_field: Mapped[TextField] = relationship(default=None, back_populates="form_field")
    checkbox_field: Mapped[CheckboxField] = relationship(default=None, back_populates="form_field")
    multi_checkbox_field: Mapped[MultiCheckboxField] = relationship(default=None, back_populates="form_field")

    form_region: Mapped["FormRegion"] = relationship(init=False, back_populates="fields")

    #
    # Custom Functions
    #
    def get_sub_field(self) -> TextField | CheckboxField | MultiCheckboxField:
        if self.text_field is not None:
            return self.text_field
        elif self.checkbox_field is not None:
            return self.checkbox_field
        elif self.multi_checkbox_field is not None:
            return self.multi_checkbox_field
        else:
            raise RuntimeError('FormField is missing subfield')
