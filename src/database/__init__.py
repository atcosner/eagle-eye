import sqlalchemy
from pathlib import Path
from sqlalchemy.orm import DeclarativeBase

from ..util.paths import LocalPaths


class OrmBase(DeclarativeBase):
    pass


# TODO: A more elegant solution?
from .job import Job
from .reference_form import ReferenceForm


def create_db(path: Path, overwrite: bool = False) -> sqlalchemy.Engine:
    engine = sqlalchemy.create_engine(f'sqlite+pysqlite:///{path}', echo=False)

    if overwrite:
        path.unlink(missing_ok=True)

    if not path.exists():
        OrmBase.metadata.create_all(engine)

    return engine


DB_ENGINE = create_db(LocalPaths.database_file(), overwrite=False)
