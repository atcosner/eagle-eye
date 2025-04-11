from pathlib import Path
from sqlalchemy.orm import Session

from src.database import DB_ENGINE, OrmBase
from src.database.reference_form import ReferenceForm
from src.database.text_field import TextField
from src.util.paths import LocalPaths
from src.util.types import BoxBounds


if LocalPaths.database_file().exists():
    LocalPaths.database_file().unlink()
    OrmBase.metadata.create_all(DB_ENGINE)


with Session(DB_ENGINE) as session:
    new_form = ReferenceForm(
        name='KU Ornithology Form v8',
        path=Path(r'C:\Users\atcos\AppData\Local\EagleEye\reference_forms\kt_field_form_v8.png'),
        alignment_mark_count=16,
        whole_page_form=False,
    )
    new_form.text_fields = [
        TextField(name='KT Number', visual_region=BoxBounds(x=248, y=120, width=120, height=44)),
        TextField(name='Prep Number', visual_region=BoxBounds(x=441, y=120, width=207, height=46)),
        TextField(name='KU Number', visual_region=BoxBounds(x=707, y=120, width=207, height=46)),
        TextField(name='OT Number', visual_region=BoxBounds(x=972, y=120, width=215, height=46)),
    ]

    session.add(new_form)
    session.commit()
