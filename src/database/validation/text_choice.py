from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, MappedAsDataclass, relationship

from .. import OrmBase


class TextChoice(MappedAsDataclass, OrmBase):
    __tablename__ = "text_choice"
    id: Mapped[int] = mapped_column(init=False, primary_key=True)

    choice: Mapped[str]

    # Relationships

    text_validator_id: Mapped[int] = mapped_column(ForeignKey("text_validator.id"), init=False)
    text_validator: Mapped["TextValidator"] = relationship(init=False, back_populates="text_choices")
