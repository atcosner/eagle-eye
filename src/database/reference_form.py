from pathlib import Path
from sqlalchemy.orm import Mapped, mapped_column, MappedAsDataclass, relationship

from . import OrmBase
from .text_field import TextField
from .job import Job
from .util import DbPath


class ReferenceForm(MappedAsDataclass, OrmBase):
    __tablename__ = "reference_form"

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    name: Mapped[str]
    path: Mapped[Path] = mapped_column(DbPath)

    alignment_mark_count: Mapped[int]
    whole_page_form: Mapped[bool]

    # Relationships

    jobs: Mapped[list[Job]] = relationship(init=False, back_populates="reference_form")
    text_fields: Mapped[list[TextField]] = relationship(init=False, back_populates="reference_form")
