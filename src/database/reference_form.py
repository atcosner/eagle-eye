from pathlib import Path
from sqlalchemy.orm import Mapped, mapped_column, MappedAsDataclass, relationship, attribute_keyed_dict

from . import OrmBase
from .job import Job
from .page_region import PageRegion
from .util import DbPath


class ReferenceForm(MappedAsDataclass, OrmBase):
    __tablename__ = "reference_form"

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    name: Mapped[str]
    path: Mapped[Path] = mapped_column(DbPath)

    alignment_mark_count: Mapped[int]
    whole_page_form: Mapped[bool]
    second_form_y_offset: Mapped[int] = mapped_column(nullable=True, default=None)

    # Relationships

    jobs: Mapped[list[Job]] = relationship(init=False, back_populates="reference_form")
    regions: Mapped[list[PageRegion]] = relationship(init=False, back_populates="reference_form")
