from sqlalchemy.orm import Session

from src.examples.fn_form_v1 import add_fn_form_v1
from src.examples.kt_form_v8 import add_kt_form_v8

from src.database import DB_ENGINE, OrmBase
from src.util.paths import LocalPaths


if LocalPaths.database_file().exists():
    LocalPaths.database_file().unlink()
    OrmBase.metadata.create_all(DB_ENGINE)


with Session(DB_ENGINE) as session:
    add_kt_form_v8(session)
    add_fn_form_v1(session)
