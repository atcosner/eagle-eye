from pathlib import Path
from sqlalchemy.orm import Mapped, mapped_column, MappedAsDataclass, relationship, attribute_keyed_dict

from src.util.types import FormLinkingMethod, FormAlignmentMethod

from . import OrmBase
from .form_region import FormRegion
from .job import Job
from .util import DbPath


class ReferenceForm(MappedAsDataclass, OrmBase):
    __tablename__ = "reference_form"

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    name: Mapped[str]
    path: Mapped[Path] = mapped_column(DbPath)

    alignment_method: Mapped[FormAlignmentMethod]
    alignment_mark_count: Mapped[int | None] = mapped_column(nullable=True)

    linking_method: Mapped[FormLinkingMethod]

    # Relationships

    jobs: Mapped[list[Job]] = relationship(init=False, back_populates="reference_form")
    regions: Mapped[dict[int, FormRegion]] = relationship(
        init=False,
        collection_class=attribute_keyed_dict("local_id"),
        back_populates="reference_form",
    )

    def alignment_description(self) -> str:
        str_name = self.alignment_method.name.replace('_', ' ').title()
        if self.alignment_method is FormAlignmentMethod.ALIGNMENT_MARKS:
            str_name += f' ({self.alignment_mark_count})'
        return str_name
