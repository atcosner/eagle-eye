from typing import NamedTuple
from sqlalchemy.orm import Mapped, mapped_column, MappedAsDataclass

from . import OrmBase


class SemanticVersion(NamedTuple):
    major: int
    minor: int
    patch: int

    def __str__(self) -> str:
        return f'{self.major}.{self.minor}.{self.patch}'


# Semantic versioning of the database schema:
#   MAJOR - incompatible schema changes
#   MINOR - backwards compatible additions
#   PATCH - backwards compatible fixes
DB_VERSION = SemanticVersion(0, 6, 0)


class DbVersion(MappedAsDataclass, OrmBase):
    __tablename__ = "db_version"

    id: Mapped[int] = mapped_column(init=False, primary_key=True)

    major: Mapped[int]
    minor: Mapped[int]
    patch: Mapped[int]

    @property
    def version(self) -> SemanticVersion:
        return SemanticVersion(self.major, self.minor, self.patch)
