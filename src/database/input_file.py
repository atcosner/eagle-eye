from pathlib import Path
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, MappedAsDataclass, relationship

from . import OrmBase
from .util import DbPath


class InputFile(MappedAsDataclass, OrmBase):
    __tablename__ = "input_file"

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    job_id = mapped_column(ForeignKey("job.id"))
    path: Mapped[Path] = mapped_column(DbPath)

    # Relationships

    job: Mapped["Job"] = relationship(init=False, back_populates="input_files")
