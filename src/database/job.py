import uuid
from sqlalchemy.orm import Mapped, mapped_column, MappedAsDataclass, relationship

from . import OrmBase
from .input_file import InputFile


class Job(MappedAsDataclass, OrmBase):
    __tablename__ = "job"

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    name: Mapped[str]
    uuid: Mapped[uuid.UUID]

    # Relationships

    input_files: Mapped[list[InputFile]] = relationship(init=False, back_populates="job")
