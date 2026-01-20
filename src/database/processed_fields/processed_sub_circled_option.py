from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, MappedAsDataclass, relationship

from .. import OrmBase


class ProcessedSubCircledOption(MappedAsDataclass, OrmBase):
    __tablename__ = "processed_sub_circled_option"

    id: Mapped[int] = mapped_column(init=False, primary_key=True)

    name: Mapped[str]
    circled: Mapped[bool]

    # Relationships
    sub_circled_option_id: Mapped[int] = mapped_column(ForeignKey("sub_circled_option.id"), init=False)
    sub_circled_option: Mapped["SubCircledOption"] = relationship()

    processed_multi_checkbox_option_id: Mapped[int] = mapped_column(ForeignKey("processed_multi_checkbox_option.id"), init=False)
    processed_multi_checkbox_option: Mapped["ProcessedMultiCheckboxOption"] = relationship(init=False, back_populates="circled_options")
