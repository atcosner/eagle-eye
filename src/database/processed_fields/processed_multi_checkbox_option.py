from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, MappedAsDataclass, relationship, attribute_keyed_dict

from .processed_sub_circled_option import ProcessedSubCircledOption
from .. import OrmBase


class ProcessedMultiCheckboxOption(MappedAsDataclass, OrmBase):
    __tablename__ = "processed_multi_checkbox_option"

    id: Mapped[int] = mapped_column(init=False, primary_key=True)

    name: Mapped[str]
    checked: Mapped[bool]

    text: Mapped[str] = mapped_column(nullable=True)
    ocr_text: Mapped[str] = mapped_column(nullable=True)

    circled_options: Mapped[dict[str, ProcessedSubCircledOption]] = relationship(
        collection_class=attribute_keyed_dict("name"),
        back_populates="processed_multi_checkbox_option",
    )

    # Relationships
    multi_checkbox_option_id: Mapped[int] = mapped_column(ForeignKey("multi_checkbox_option.id"), init=False)
    multi_checkbox_option: Mapped["MultiCheckboxOption"] = relationship()

    processed_multi_checkbox_field_id: Mapped[int] = mapped_column(ForeignKey("processed_multi_checkbox_field.id"), init=False)
    processed_multi_checkbox_field: Mapped["ProcessedMultiCheckboxField"] = relationship(init=False, back_populates="checkboxes")
