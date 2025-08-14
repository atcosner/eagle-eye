import logging
import shutil
from pathlib import Path
from sqlalchemy.orm import Session

from src.database.copy import duplicate_field
from src.database.exporters.text_exporter import TextExporter
from src.database.fields.checkbox_field import CheckboxField
from src.database.fields.form_field import FormField
from src.database.fields.multi_checkbox_field import MultiCheckboxField
from src.database.fields.multi_checkbox_option import MultiCheckboxOption
from src.database.fields.text_field import TextField
from src.database.form_region import FormRegion
from src.database.reference_form import ReferenceForm
from src.database.validation.text_choice import TextChoice
from src.database.validation.text_validator import TextValidator
from src.util.paths import LocalPaths
from src.util.types import BoxBounds, FormLinkingMethod, FormAlignmentMethod
from src.util.validation import MultiCheckboxValidation, TextValidatorDatatype

logger = logging.getLogger(__name__)

BOTTOM_HALF_Y_OFFSET = 842
FORM_BLANK_IMAGE_PATH = Path(__file__).parent / 'kt_field_form_v8.png'
assert FORM_BLANK_IMAGE_PATH.exists(), f'Form blank reference image does not exist: {FORM_BLANK_IMAGE_PATH}'
SPECIES_LIST_PATH = Path(__file__).parent / 'ku_orn_taxonomy_reference.csv'
assert SPECIES_LIST_PATH.exists(), f'Species list does not exist: {SPECIES_LIST_PATH}'


def _read_species_list(path: Path) -> set[str]:
    with path.open('r') as file:
        return {line.lower().strip() for line in file.readlines()}


def add_kt_form_v8(session: Session) -> None:
    # read in the KT form species list
    species_list = _read_species_list(SPECIES_LIST_PATH)

    form = ReferenceForm(
        name='KU Ornithology - KT Form v8',
        path=LocalPaths.reference_forms_directory() / FORM_BLANK_IMAGE_PATH.name,
        alignment_method=FormAlignmentMethod.ALIGNMENT_MARKS,
        alignment_mark_count=16,
        linking_method=FormLinkingMethod.PREVIOUS_REGION,
    )

    # copy the reference form into our working dir
    if not form.path.exists():
        shutil.copy(FORM_BLANK_IMAGE_PATH, form.path)

    top_region = FormRegion(local_id=0, name='Top')
    top_region.fields = [
        FormField(
            identifier=True,
            identifier_regex=r'^(?P<id>[0-9]{5})$',
            text_field=TextField(
                name='KT Number',
                visual_region=BoxBounds(x=248, y=120, width=120, height=44),
                text_exporter=TextExporter(prefix='KT_'),
                text_validator=TextValidator(
                    text_regex=r'^[0-9]{5}$',
                    error_tooltip='KT Numbers must be exactly 5 digits',
                ),
            ),
        ),

        FormField(
            text_field=TextField(
                name='Prep Number',
                visual_region=BoxBounds(x=441, y=120, width=207, height=46),
                text_validator=TextValidator(
                    text_regex=r'^[A-Z]{2,4} [0-9]{3,5}$',
                    error_tooltip='Prep Number must be 2-4 capital letters followed by a number with 3-5 digits',
                ),
            ),
        ),
        FormField(
            text_field=TextField(
                name='KU Number',
                visual_region=BoxBounds(x=707, y=120, width=207, height=46),
                text_exporter=TextExporter(no_export=True),
            ),
        ),
        FormField(
            text_field=TextField(
                name='OT Number',
                visual_region=BoxBounds(x=972, y=120, width=215, height=46),
                text_exporter=TextExporter(no_export=True),
            ),
        ),

        FormField(
            text_field=TextField(
                name='Locality',
                visual_region=BoxBounds(x=249, y=183, width=992, height=39),
                allow_copy=True,
                text_exporter=TextExporter(export_field_name='locality_string'),
                # This is not using a custom datatype to text the regex functionality
                # - Something complicated like this should probably be a custom datatype
                text_validator=TextValidator(
                    text_regex=(
                        r"^(?P<state>[a-zA-Z-]{2,}(?:[ ,-]+[a-zA-Z-]{2,})*)"
                        r" ?: ?(?P<county>[a-zA-Z-]{2,}(?:[ ,-]+[a-zA-Z-]{2,})*)"
                        r" ?: ?(?P<location>[a-zA-Z-]{2,}(?:[ ,-]+[a-zA-Z-]{2,})*)$"
                    ),
                    reformat_regex='{state} : {county} : {location}',
                    error_tooltip='Locality must be in the format: [STATE] : [COUNTY] : [PLACE]',
                ),
            ),
        ),

        FormField(
            text_field=TextField(
                name='GPS Waypoint',
                visual_region=BoxBounds(x=860, y=224, width=164, height=34),
                allow_copy=True,
                text_validator=TextValidator(
                    datatype=TextValidatorDatatype.KU_GPS_WAYPOINT,
                    text_required=False,
                ),
            ),
        ),
        FormField(
            text_field=TextField(
                name='Latitude',
                visual_region=BoxBounds(x=210, y=227, width=250, height=31),
                text_validator=TextValidator(
                    datatype=TextValidatorDatatype.GPS_POINT_DD,
                    text_required=False,
                ),
            ),
        ),
        FormField(
            text_field=TextField(
                name='Longitude',
                visual_region=BoxBounds(x=511, y=225, width=253, height=33),
                text_validator=TextValidator(
                    datatype=TextValidatorDatatype.GPS_POINT_DD,
                    text_required=False,
                ),
            ),
        ),
        FormField(
            text_field=TextField(
                name='Error',
                visual_region=BoxBounds(x=1120, y=225, width=108, height=33),
                text_validator=TextValidator(
                    datatype=TextValidatorDatatype.INTEGER,
                    text_required=False,
                ),
            ),
        ),

        FormField(
            text_field=TextField(
                name='Species',
                visual_region=BoxBounds(x=253, y=262, width=594, height=33),
                allow_copy=True,
                text_validator=TextValidator(
                    datatype=TextValidatorDatatype.LIST_CHOICE,
                    allow_closest_match_correction=True,
                    text_choices=[TextChoice(text=t) for t in species_list],
                ),
            ),
        ),
        FormField(
            text_field=TextField(
                name='Coordinate Source',
                visual_region=BoxBounds(x=997, y=262, width=235, height=33),
                allow_copy=True,
            ),
        ),

        FormField(
            text_field=TextField(
                name='Collection Date',
                visual_region=BoxBounds(x=274, y=300, width=411, height=32),
                allow_copy=True,
                text_validator=TextValidator(
                    datatype=TextValidatorDatatype.DATE,
                ),
            ),
        ),
        FormField(
            text_field=TextField(
                name='Collector',
                visual_region=BoxBounds(x=790, y=299, width=435, height=33),
                allow_copy=True,
                text_validator=TextValidator(
                    datatype=TextValidatorDatatype.RAW_TEXT,
                    text_regex=r'^[A-Z]{2,4}$',
                    error_tooltip='Initials should be two to four capital letters',
                ),
            ),
        ),

        FormField(
            text_field=TextField(
                name='Habitat',
                visual_region=BoxBounds(x=217, y=336, width=1012, height=32),
                allow_copy=True,
                text_validator=TextValidator(),
            ),
        ),

        FormField(
            multi_checkbox_field=MultiCheckboxField(
                name='Collection Method',
                visual_region=BoxBounds(x=163, y=376, width=1061, height=35),
                validator=MultiCheckboxValidation.REQUIRE_ONE,
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
            )
        ),

        FormField(
            text_field=TextField(
                name='Iris',
                visual_region=BoxBounds(x=157, y=413, width=379, height=40),
                allow_copy=True,
                # validator=Iris,
                text_regions=[BoxBounds(x=287, y=411, width=247, height=32)],
                checkbox_region=BoxBounds(x=213, y=424, width=13, height=13),
                checkbox_text='dark brown',
                text_validator=TextValidator(),
            )
        ),
        FormField(
            text_field=TextField(
                name='Bill',
                visual_region=BoxBounds(x=577, y=412, width=648, height=31),
                allow_copy=True,
            ),
        ),

        FormField(
            text_field=TextField(
                name='Feet/Legs',
                visual_region=BoxBounds(x=242, y=450, width=726, height=30),
                allow_copy=True,
            ),
        ),
        FormField(
            text_field=TextField(
                name='Weight',
                visual_region=BoxBounds(x=1035, y=447, width=190, height=33),
                text_validator=TextValidator(
                    datatype=TextValidatorDatatype.INTEGER_OR_FLOAT,
                ),
            ),
        ),

        FormField(
            multi_checkbox_field=MultiCheckboxField(
                name='Tissue Date',
                visual_region=BoxBounds(x=160, y=488, width=283, height=35),
                validator=MultiCheckboxValidation.REQUIRE_ONE,
                checkboxes=[
                    MultiCheckboxOption(name='Collection', region=BoxBounds(x=280, y=498, width=13, height=13)),
                    MultiCheckboxOption(name='Preparation', region=BoxBounds(x=360, y=498, width=13, height=13)),
                ],
            )
        ),
        FormField(
            text_field=TextField(
                name='Time of Death',
                visual_region=BoxBounds(x=637, y=484, width=161, height=33),
                text_validator=TextValidator(
                    datatype=TextValidatorDatatype.TIME,
                ),
            ),
        ),
        FormField(
            text_field=TextField(
                name='Time of Tissue Preservation',
                visual_region=BoxBounds(x=797, y=485, width=423, height=40),
                text_regions=[BoxBounds(x=988, y=486, width=154, height=31)],
                checkbox_region=BoxBounds(x=1150, y=498, width=13, height=13),
                checkbox_text='unknown',
                # TODO: Should text with a checkbox be handled differently?
                text_validator=TextValidator(
                    datatype=TextValidatorDatatype.TIME,
                    text_required=False,
                ),
            )
        ),

        FormField(
            text_field=TextField(
                name='Tissues',
                visual_region=BoxBounds(x=251, y=520, width=147, height=35),
                text_validator=TextValidator(
                    datatype=TextValidatorDatatype.CSV_OF_CHOICE,
                    text_choices=[
                        TextChoice(text='M'),
                        TextChoice(text='L'),
                        TextChoice(text='G'),
                        TextChoice(text='H'),
                    ],
                ),
            ),
        ),
        FormField(
            text_field=TextField(
                name='No. Tubes',
                visual_region=BoxBounds(x=509, y=523, width=56, height=32),
                text_validator=TextValidator(
                    datatype=TextValidatorDatatype.INTEGER,
                ),
            ),
        ),
        FormField(
            multi_checkbox_field=MultiCheckboxField(
                name='Tissue Preservation',
                visual_region=BoxBounds(x=569, y=527, width=669, height=33),
                validator=MultiCheckboxValidation.REQUIRE_ONE,
                checkboxes=[
                    MultiCheckboxOption(name='-20C', region=BoxBounds(x=693, y=536, width=13, height=13)),
                    MultiCheckboxOption(name='-80C', region=BoxBounds(x=791, y=536, width=13, height=13)),
                    MultiCheckboxOption(name='LN2', region=BoxBounds(x=889, y=536, width=13, height=13)),
                    MultiCheckboxOption(name='Ethanol', region=BoxBounds(x=970, y=536, width=13, height=13)),
                    MultiCheckboxOption(
                        name='Other',
                        region=BoxBounds(x=1065, y=536, width=13, height=13),
                        text_region=BoxBounds(x=1145, y=526, width=84, height=29),
                    ),
                ],
            )
        ),

        FormField(
            text_field=TextField(
                name='Prep Date',
                visual_region=BoxBounds(x=279, y=560, width=378, height=32),
                text_validator=TextValidator(
                    datatype=TextValidatorDatatype.DATE,
                ),
            ),
        ),
        FormField(
            text_field=TextField(
                name='Preparator',
                visual_region=BoxBounds(x=776, y=562, width=451, height=30),
                text_validator=TextValidator(
                    datatype=TextValidatorDatatype.RAW_TEXT,
                    text_regex=r'^[A-Z]{2,4}$',
                    error_tooltip='Initials should be two to four capital letters',
                ),
            ),
        ),

        FormField(
            multi_checkbox_field=MultiCheckboxField(
                name='Prep',
                visual_region=BoxBounds(x=158, y=600, width=1077, height=36),
                validator=MultiCheckboxValidation.REQUIRE_ONE,
                checkboxes=[
                    MultiCheckboxOption(name='Round Skin', region=BoxBounds(x=242, y=610, width=13, height=13)),
                    MultiCheckboxOption(name='Skeleton', region=BoxBounds(x=385, y=610, width=13, height=13)),
                    MultiCheckboxOption(name='Partial Skeleton', region=BoxBounds(x=508, y=610, width=13, height=13)),
                    MultiCheckboxOption(name='Wingspread', region=BoxBounds(x=657, y=610, width=13, height=13)),
                    MultiCheckboxOption(name='Alcohol', region=BoxBounds(x=811, y=610, width=13, height=13)),
                    MultiCheckboxOption(
                        name='Other',
                        region=BoxBounds(x=887, y=610, width=13, height=13),
                        text_region=BoxBounds(x=971, y=597, width=258, height=32),
                    ),
                ],
            )
        ),

        FormField(
            text_field=TextField(
                name='Molt',
                visual_region=BoxBounds(x=220, y=634, width=1004, height=32),
                text_validator=TextValidator(),
            ),
        ),

        FormField(
            text_field=TextField(
                name='Gonads',
                visual_region=BoxBounds(x=255, y=671, width=967, height=31),
                text_validator=TextValidator(),
            ),
        ),

        FormField(
            text_field=TextField(
                name='Skull',
                visual_region=BoxBounds(x=222, y=706, width=257, height=34),
                text_validator=TextValidator(),
            ),
        ),
        FormField(
            multi_checkbox_field=MultiCheckboxField(
                name='Fat',
                visual_region=BoxBounds(x=479, y=706, width=384, height=41),
                validator=MultiCheckboxValidation.REQUIRE_ONE,
                checkboxes=[
                    MultiCheckboxOption(name='None', region=BoxBounds(x=536, y=721, width=13, height=13)),
                    MultiCheckboxOption(name='Light', region=BoxBounds(x=599, y=721, width=13, height=13)),
                    MultiCheckboxOption(name='Moderate', region=BoxBounds(x=658, y=721, width=13, height=13)),
                    MultiCheckboxOption(name='Heavy', region=BoxBounds(x=724, y=721, width=13, height=13)),
                    MultiCheckboxOption(name='Very Heavy', region=BoxBounds(x=787, y=721, width=13, height=13)),
                ],
            )
        ),
        FormField(
            text_field=TextField(
                name='Bursa',
                visual_region=BoxBounds(x=980, y=709, width=243, height=31),
                text_validator=TextValidator(),
            ),
        ),

        FormField(
            text_field=TextField(
                name='Stomach',
                visual_region=BoxBounds(x=232, y=745, width=992, height=32),
                text_validator=TextValidator(),
            ),
        ),

        FormField(
            multi_checkbox_field=MultiCheckboxField(
                name='Sex',
                visual_region=BoxBounds(x=162, y=786, width=329, height=31),
                validator=MultiCheckboxValidation.REQUIRE_ONE,
                checkboxes=[
                    MultiCheckboxOption(name='Female', region=BoxBounds(x=222, y=795, width=13, height=13)),
                    MultiCheckboxOption(name='Male', region=BoxBounds(x=329, y=795, width=13, height=13)),
                    MultiCheckboxOption(name='Unknown', region=BoxBounds(x=418, y=795, width=13, height=13)),
                ],
            )
        ),
        FormField(
            text_field=TextField(
                name='Age',
                visual_region=BoxBounds(x=579, y=783, width=315, height=31),
                text_validator=TextValidator(),
            ),
        ),
        FormField(
            multi_checkbox_field=MultiCheckboxField(
                name='Parasites Collected',
                visual_region=BoxBounds(x=895, y=787, width=333, height=29),
                validator=MultiCheckboxValidation.OPTIONAL,
                checkboxes=[
                    MultiCheckboxOption(name='Ecto', region=BoxBounds(x=1054, y=795, width=13, height=13)),
                    MultiCheckboxOption(name='Endo', region=BoxBounds(x=1143, y=795, width=13, height=13)),
                ],
            )
        ),

        FormField(
            text_field=TextField(
                name='Remarks',
                visual_region=BoxBounds(x=160, y=824, width=1067, height=73),
                text_regions=[
                    BoxBounds(x=265, y=816, width=962, height=35),
                    BoxBounds(x=162, y=856, width=937, height=32),
                ],
            )
        ),
        FormField(
            checkbox_field=CheckboxField(
                name='See Back',
                visual_region=BoxBounds(x=1095, y=855, width=133, height=40),
                checkbox_region=BoxBounds(x=1104, y=869, width=13, height=13),
            )
        ),

        FormField(
            multi_checkbox_field=MultiCheckboxField(
                name='Photos',
                visual_region=BoxBounds(x=162, y=898, width=259, height=35),
                validator=MultiCheckboxValidation.OPTIONAL,
                checkboxes=[
                    MultiCheckboxOption(name='Habitat', region=BoxBounds(x=253, y=907, width=13, height=13)),
                    MultiCheckboxOption(name='Specimen', region=BoxBounds(x=334, y=907, width=13, height=13)),
                ],
            )
        ),
        FormField(
            checkbox_field=CheckboxField(
                name='Audio',
                visual_region=BoxBounds(x=471, y=899, width=93, height=30),
                checkbox_region=BoxBounds(x=479, y=907, width=13, height=13),
            )
        ),
        FormField(
            multi_checkbox_field=MultiCheckboxField(
                name='Parasite Presence',
                visual_region=BoxBounds(x=612, y=897, width=408, height=33),
                validator=MultiCheckboxValidation.OPTIONAL,
                checkboxes=[
                    MultiCheckboxOption(name='70%', region=BoxBounds(x=773, y=907, width=13, height=13)),
                    MultiCheckboxOption(name='80%', region=BoxBounds(x=858, y=907, width=13, height=13)),
                    MultiCheckboxOption(name='95%', region=BoxBounds(x=944, y=907, width=13, height=13)),
                ],
            )
        ),
        FormField(
            checkbox_field=CheckboxField(
                name='Washed',
                visual_region=BoxBounds(x=1067, y=898, width=119, height=31),
                checkbox_region=BoxBounds(x=1076, y=907, width=13, height=13)
            )
        ),
    ]
    form.regions[top_region.local_id] = top_region
    session.commit()

    # Duplicate with an offset for the bottom region
    bottom_region = FormRegion(local_id=1, name='Bottom')
    bottom_region.fields = [
        duplicate_field(field, remove_copy=True, y_offset=BOTTOM_HALF_Y_OFFSET) for field in top_region.fields
    ]
    form.regions[bottom_region.local_id] = bottom_region

    session.add(form)
    session.commit()
