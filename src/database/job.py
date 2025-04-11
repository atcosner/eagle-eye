import uuid
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, MappedAsDataclass, relationship

from . import OrmBase
from .input_file import InputFile


class Job(MappedAsDataclass, OrmBase):
    __tablename__ = "job"

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    reference_form_id: Mapped[int] = mapped_column(ForeignKey("reference_form.id"), init=False, nullable=True)

    name: Mapped[str]
    uuid: Mapped[uuid.UUID]

    # Relationships

    reference_form: Mapped["ReferenceForm"] = relationship(init=False, back_populates="jobs")
    input_files: Mapped[list[InputFile]] = relationship(init=False, back_populates="job")
