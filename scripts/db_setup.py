from sqlalchemy.orm import Session

from src.util.paths import LocalPaths

# importing the DB_ENGINE will create the DB if it needs to
if LocalPaths.database_file().exists():
    LocalPaths.database_file().unlink()

from src.database import DB_ENGINE
from src.examples.fn_form_v1 import add_fn_form_v1
from src.examples.kt_form_v8 import add_kt_form_v8

with Session(DB_ENGINE) as session:
    add_kt_form_v8(session)
    # add_fn_form_v1(session)
