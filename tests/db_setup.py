from pathlib import Path
from sqlalchemy.orm import Session

from src.database import DB_ENGINE, OrmBase
from src.database.fields.checkbox_field import CheckboxField
from src.database.fields.form_fields import FormField
from src.database.fields.multi_checkbox_field import MultiCheckboxField
from src.database.fields.multi_checkbox_option import MultiCheckboxOption
from src.database.fields.multiline_text_field import MultilineTextField
from src.database.fields.text_field import TextField
from src.database.reference_form import ReferenceForm
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
    new_form.fields = [
        FormField(text_field=TextField(name='KT Number', visual_region=BoxBounds(x=248, y=120, width=120, height=44))),
        FormField(text_field=TextField(name='Prep Number', visual_region=BoxBounds(x=441, y=120, width=207, height=46))),
        FormField(text_field=TextField(name='KU Number', visual_region=BoxBounds(x=707, y=120, width=207, height=46))),
        FormField(text_field=TextField(name='OT Number', visual_region=BoxBounds(x=972, y=120, width=215, height=46))),
        FormField(
            multi_checkbox_field=MultiCheckboxField(
                name='Collection Method',
                visual_region=BoxBounds(x=163, y=376, width=1061, height=35),
                checkboxes=[
                    MultiCheckboxOption(name='Shot', region=BoxBounds(x=308, y=387, width=13, height=13)),
                    MultiCheckboxOption(name='Net/Trap', region=BoxBounds(x=391, y=387, width=13, height=13)),
                    MultiCheckboxOption(name='Salvage', region=BoxBounds(x=520, y=387, width=13, height=13)),
                    MultiCheckboxOption(name='Unknown', region=BoxBounds(x=637, y=387, width=13, height=13)),
                    MultiCheckboxOption(
                        name='Other',
                        region=BoxBounds(x=720, y=387, width=13, height=13),
                        text_region=BoxBounds(x=801, y=372, width=420, height=34),
                    ),
                ],
            ),
        ),
        FormField(
            checkbox_field=CheckboxField(
                name='See Back',
                visual_region=BoxBounds(x=1095, y=855, width=133, height=40),
                checkbox_region=BoxBounds(x=1104, y=869, width=13, height=13),
            ),
        ),
        FormField(
            multiline_text_field=MultilineTextField(
                name='Remarks',
                visual_region=BoxBounds(x=160, y=824, width=1067, height=73),
                line_regions=[
                    BoxBounds(x=265, y=816, width=962, height=35),
                    BoxBounds(x=162, y=856, width=937, height=32),
                ],
            ),
        )
    ]

    session.add(new_form)
    session.commit()
