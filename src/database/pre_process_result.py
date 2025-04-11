from pathlib import Path
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, MappedAsDataclass, relationship

from . import OrmBase
from .util import DbPath


class PreProcessResult(MappedAsDataclass, OrmBase):
    __tablename__ = "pre_process_result"

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    input_file_id: Mapped[int] = mapped_column(ForeignKey("input_file.id"), init=False)

    rotation_angle: Mapped[int]
    detected_alignment_marks: Mapped[int]
    image_path: Mapped[Path] = mapped_column(DbPath)

    # Relationships

    input_file: Mapped["InputFile"] = relationship(init=False, back_populates="pre_process_results")
