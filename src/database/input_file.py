from pathlib import Path
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, MappedAsDataclass, relationship

from . import OrmBase
from .util import DbPath
from .pre_processing.pre_process_result import PreProcessResult
from .process_result import ProcessResult


class InputFile(MappedAsDataclass, OrmBase):
    __tablename__ = "input_file"

    id: Mapped[int] = mapped_column(init=False, primary_key=True)

    path: Mapped[Path] = mapped_column(DbPath)
    container_file: Mapped[bool] = mapped_column(default=False)
    linked_input_file_id: Mapped[int] = mapped_column(nullable=True, default=None)

    # Relationships

    job_id: Mapped[int] = mapped_column(ForeignKey("job.id"), init=False)
    job: Mapped["Job"] = relationship(init=False, back_populates="input_files")

    pre_process_result: Mapped[PreProcessResult] = relationship(init=False, back_populates="input_file")
    process_result: Mapped[ProcessResult] = relationship(init=False, back_populates="input_file")
