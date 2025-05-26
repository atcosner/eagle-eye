from pathlib import Path
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, MappedAsDataclass, relationship

from . import OrmBase
from .pre_process_result import PreProcessResult
from .process_result import ProcessResult
from .util import DbPath


class InputFile(MappedAsDataclass, OrmBase):
    __tablename__ = "input_file"

    id: Mapped[int] = mapped_column(init=False, primary_key=True)

    path: Mapped[Path] = mapped_column(DbPath)
    linked_input_file: Mapped[int] = mapped_column(nullable=True, default=None)

    # Relationships

    job_id: Mapped[int] = mapped_column(ForeignKey("job.id"), init=False)
    job: Mapped["Job"] = relationship(init=False, back_populates="input_files")

    pre_process_result: Mapped[PreProcessResult] = relationship(init=False, back_populates="input_file")
    process_result: Mapped[ProcessResult] = relationship(init=False, back_populates="input_file")
