from pathlib import Path
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, MappedAsDataclass, relationship

from .. import OrmBase
from ..util import DbPath


class RotationAttempt(MappedAsDataclass, OrmBase):
    __tablename__ = "rotation_attempt"

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    pre_process_result_id: Mapped[int] = mapped_column(ForeignKey("pre_process_result.id"), init=False)

    rotation_angle: Mapped[float]
    path: Mapped[Path] = mapped_column(DbPath)

    # Relationships

    pre_process_result: Mapped["PreProcessResult"] = relationship(init=False, back_populates="rotation_attempts")
