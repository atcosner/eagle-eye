import sqlalchemy
from pathlib import Path
from sqlalchemy.orm import DeclarativeBase, Session

from ..util.paths import LocalPaths


class OrmBase(DeclarativeBase):
    pass


# TODO: A more elegant solution?
from .job import Job
from .reference_form import ReferenceForm
from .version import DbVersion, SemanticVersion, DB_VERSION


def read_db_version(engine: sqlalchemy.Engine) -> SemanticVersion | None:
    try:
        with Session(engine) as session:
            row = session.scalars(sqlalchemy.select(DbVersion)).first()
            return row.version if row is not None else None
    except sqlalchemy.exc.OperationalError:
        # the version table does not exist (database predates versioning)
        return None


def create_db(path: Path, overwrite: bool = False) -> sqlalchemy.Engine:
    engine = sqlalchemy.create_engine(f'sqlite+pysqlite:///{path}', echo=False)

    if overwrite:
        path.unlink(missing_ok=True)

    if not path.exists():
        OrmBase.metadata.create_all(engine)

        # ensure the new database starts with a version
        with Session(engine) as session:
            session.add(DbVersion(*DB_VERSION))
            session.commit()

    return engine


DB_ENGINE = create_db(LocalPaths.database_file(), overwrite=False)
