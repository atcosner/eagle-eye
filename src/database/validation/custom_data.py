from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, MappedAsDataclass, relationship

from .text_choice import TextChoice
from .. import OrmBase


class CustomData(MappedAsDataclass, OrmBase):
    __tablename__ = "custom_data"

    id: Mapped[int] = mapped_column(init=False, primary_key=True)

    key: Mapped[int]

    # Relationships

    text_choices: Mapped[list[TextChoice]] = relationship(default_factory=list, back_populates="custom_data")

    text_validator_id: Mapped[int] = mapped_column(ForeignKey("text_validator.id"), init=False)
    text_validator: Mapped["TextValidator"] = relationship(init=False, back_populates="custom_data")
