from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, MappedAsDataclass, relationship

from . import OrmBase


class InputFile(MappedAsDataclass, OrmBase):
    __tablename__ = "input_file"

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    job_id: Mapped[int] = mapped_column(ForeignKey("job.id"))
    path: Mapped[str]  # Path

    # Relationships

    job: Mapped["Job"] = relationship(init=False, back_populates="input_files")
