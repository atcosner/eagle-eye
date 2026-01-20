from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, MappedAsDataclass, relationship

from src.util.types import BoxBounds

from .. import OrmBase
from ..util import DbBoxBounds


class SubCircledOption(MappedAsDataclass, OrmBase):
    __tablename__ = "sub_circled_option"

    id: Mapped[int] = mapped_column(init=False, primary_key=True)

    name: Mapped[str]
    region: Mapped[BoxBounds] = mapped_column(DbBoxBounds)

    # Relationships

    multi_checkbox_option_id: Mapped[int] = mapped_column(ForeignKey("multi_checkbox_option.id"), init=False)
    multi_checkbox_option: Mapped["MultiCheckboxOption"] = relationship(init=False, back_populates="circled_options")
