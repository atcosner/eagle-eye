from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, MappedAsDataclass, relationship

from .. import OrmBase


class TextChoice(MappedAsDataclass, OrmBase):
    __tablename__ = "text_choice"
    id: Mapped[int] = mapped_column(init=False, primary_key=True)

    text: Mapped[str]

    # Relationships

    text_validator_id: Mapped[int | None] = mapped_column(ForeignKey("text_validator.id"), init=False)
    text_validator: Mapped["TextValidator"] = relationship(init=False, back_populates="text_choices")

    custom_data_id: Mapped[int | None] = mapped_column(ForeignKey("custom_data.id"), init=False)
    custom_data: Mapped["CustomData"] = relationship(init=False, back_populates="text_choices")
