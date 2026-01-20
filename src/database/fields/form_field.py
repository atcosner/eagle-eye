from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, MappedAsDataclass, relationship

from .circled_field import CircledField
from .checkbox_field import CheckboxField
from .multi_checkbox_field import MultiCheckboxField
from .text_field import TextField
from .. import OrmBase


class FormField(MappedAsDataclass, OrmBase):
    __tablename__ = "form_field"

    id: Mapped[int] = mapped_column(init=False, primary_key=True)

    identifier: Mapped[bool] = mapped_column(default=False)
    identifier_regex: Mapped[str] = mapped_column(nullable=True, default=None)

    # Relationships

    text_field: Mapped[TextField] = relationship(default=None, back_populates="form_field")
    checkbox_field: Mapped[CheckboxField] = relationship(default=None, back_populates="form_field")
    multi_checkbox_field: Mapped[MultiCheckboxField] = relationship(default=None, back_populates="form_field")
    circled_field: Mapped[CircledField] = relationship(default=None, back_populates="form_field")

    field_group_id: Mapped[int] = mapped_column(ForeignKey("field_group.id"), init=False)
    field_group: Mapped["FieldGroup"] = relationship(init=False, back_populates="fields")

    #
    # Custom Functions
    #
    def get_sub_field(self) -> TextField | CheckboxField | MultiCheckboxField | CircledField:
        if self.text_field is not None:
            return self.text_field
        elif self.checkbox_field is not None:
            return self.checkbox_field
        elif self.multi_checkbox_field is not None:
            return self.multi_checkbox_field
        elif self.circled_field is not None:
            return self.circled_field
        else:
            raise RuntimeError('FormField is missing subfield')
