import uuid
from sqlalchemy.orm import Mapped, mapped_column, MappedAsDataclass

from . import OrmBase


class Job(MappedAsDataclass, OrmBase):
    __tablename__ = "job"

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    name: Mapped[str]
    uuid: Mapped[uuid.UUID]
