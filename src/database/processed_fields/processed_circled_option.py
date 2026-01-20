from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, MappedAsDataclass, relationship

from .. import OrmBase


class ProcessedCircledOption(MappedAsDataclass, OrmBase):
    __tablename__ = "processed_circled_option"

    id: Mapped[int] = mapped_column(init=False, primary_key=True)

    name: Mapped[str]
    circled: Mapped[bool]

    # Relationships
    circled_option_id: Mapped[int] = mapped_column(ForeignKey("circled_option.id"), init=False)
    circled_option: Mapped["CircledOption"] = relationship()

    processed_circled_field_id: Mapped[int] = mapped_column(ForeignKey("processed_circled_field.id"), init=False)
    processed_circled_field: Mapped["ProcessedCircledField"] = relationship(init=False, back_populates="options")
