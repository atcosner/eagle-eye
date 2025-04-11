from pathlib import Path
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, MappedAsDataclass, relationship, attribute_keyed_dict

from . import OrmBase
from .rotation_attempt import RotationAttempt
from .util import DbPath


class PreProcessResult(MappedAsDataclass, OrmBase):
    __tablename__ = "pre_process_result"

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    input_file_id: Mapped[int] = mapped_column(ForeignKey("input_file.id"), init=False)

    successful_match: Mapped[bool]
    accepted_rotation_angle: Mapped[int] = mapped_column(init=False, default=None, nullable=True)
    matches_image_path: Mapped[Path] = mapped_column(DbPath, init=False, default=None, nullable=True)
    aligned_image_path: Mapped[Path] = mapped_column(DbPath, init=False, default=None, nullable=True)
    overlaid_image_path: Mapped[Path] = mapped_column(DbPath, init=False, default=None, nullable=True)

    # Relationships

    input_file: Mapped["InputFile"] = relationship(init=False, back_populates="pre_process_result")
    rotation_attempts: Mapped[dict[int, RotationAttempt]] = relationship(
        init=False,
        collection_class=attribute_keyed_dict("rotation_angle"),
        back_populates="pre_process_result",
    )
