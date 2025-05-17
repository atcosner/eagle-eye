import copy
import shutil
from pathlib import Path
from sqlalchemy.orm import Session

from src.database import DB_ENGINE, OrmBase
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
from src.util.types import BoxBounds, FormLinkingMethod
from src.util.validation import MultiCheckboxValidation, TextValidatorDatatype


def offset_object(item: object, y_offset: int) -> object | None:
    if isinstance(item, BoxBounds):
        new_item = copy.copy(item)
        return new_item._replace(y=item.y + y_offset)
    elif isinstance(item, list):
        return [offset_object(part, y_offset) for part in item if offset_object(part, y_offset) is not None]
    else:
        return None


def create_field_with_offset(field: FormField, y_offset: int) -> FormField:
    if field.text_field is not None:
        new_exporter = None
        if field.text_field.text_exporter is not None:
            exporter = field.text_field.text_exporter
            new_exporter = TextExporter(
                no_export=exporter.no_export,
                export_field_name=exporter.export_field_name,
                prefix=exporter.prefix,
                suffix=exporter.suffix,
                strip_value=exporter.strip_value,
            )

        new_validator = None
        if field.text_field.text_validator is not None:
            validator = field.text_field.text_validator
            new_validator = TextValidator(
                datatype=validator.datatype,
                text_required=validator.text_required,
                text_regex=validator.text_regex,
                reformat_regex=validator.reformat_regex,
                error_tooltip=validator.error_tooltip,
                text_choices=[TextChoice(c.text) for c in validator.text_choices],
            )

        # Remove allow_copy from the previous field
        allow_copy = field.text_field.allow_copy
        if allow_copy:
            field.text_field.allow_copy = False

        text_regions = [offset_object(x, y_offset) for x in field.text_field.text_regions] if field.text_field.text_regions is not None else None

        new_field = TextField(
            name=field.text_field.name,
            visual_region=offset_object(field.text_field.visual_region, y_offset),
            checkbox_region=offset_object(field.text_field.checkbox_region, y_offset),
            text_regions=text_regions,
            checkbox_text=field.text_field.checkbox_text,
            allow_copy=allow_copy,
            text_exporter=new_exporter,
            text_validator=new_validator,
        )
        return FormField(
            identifier=field.identifier,
            identifier_regex=field.identifier_regex,
            text_field=new_field,
        )

    elif field.checkbox_field is not None:
        new_field = CheckboxField(
            name=field.checkbox_field.name,
            visual_region=offset_object(field.checkbox_field.visual_region, y_offset),
            checkbox_region=offset_object(field.checkbox_field.checkbox_region, y_offset),
        )
        return FormField(checkbox_field=new_field)

    elif field.multi_checkbox_field is not None:
        checkboxes = []
        for checkbox in field.multi_checkbox_field.checkboxes:
            checkboxes.append(
                MultiCheckboxOption(
                    name=checkbox.name,
                    region=offset_object(checkbox.region, y_offset),
                    text_region=offset_object(checkbox.text_region, y_offset),
                )
            )

        new_field = MultiCheckboxField(
            name=field.multi_checkbox_field.name,
            visual_region=offset_object(field.multi_checkbox_field.visual_region, y_offset),
            validator=field.multi_checkbox_field.validator,
            checkboxes=checkboxes,
        )
        return FormField(multi_checkbox_field=new_field)

    else:
        return None


if LocalPaths.database_file().exists():
    LocalPaths.database_file().unlink()
    OrmBase.metadata.create_all(DB_ENGINE)


# Determine the location of the project directory
file_path = Path(__file__)
project_path = None
for parent in file_path.parents:
    if parent.name == 'eagle-eye-qt':
        project_path = parent
        break
print(f'Project path: {project_path}')


def _read_species_list(path: Path) -> set[str]:
    with path.open('r') as file:
        return {line.lower().strip() for line in file.readlines()}


# Read in the list of species on import
species_list = project_path / 'src' / 'eagle-eye' / 'validation' / 'ku_orn_taxonomy_reference.csv'
ORNITHOLOGY_SPECIES_LIST = _read_species_list(species_list)


# Copy the reference image into the working diectory
reference_forms = LocalPaths.reference_forms_directory()
reference_forms.mkdir(exist_ok=True)

REFERENCE_FORM_FILENAME = 'kt_field_form_v8.png'
shutil.copy(
    project_path / 'src' / 'eagle-eye' / 'form_templates' / 'production' / REFERENCE_FORM_FILENAME,
    reference_forms / REFERENCE_FORM_FILENAME,
)

with Session(DB_ENGINE) as session:
    new_form = ReferenceForm(
        name='KU Ornithology Form v8',
        path=reference_forms / REFERENCE_FORM_FILENAME,
        alignment_mark_count=16,
        linking_method=FormLinkingMethod.PREVIOUS_REGION,
    )

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
                    text_choices=[TextChoice(text=t) for t in ORNITHOLOGY_SPECIES_LIST]
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
    new_form.regions[top_region.local_id] = top_region
    session.commit()

    # Duplicate with an offset for the bottom region
    BOTTOM_HALF_Y_OFFSET = 842
    bottom_region = FormRegion(local_id=1, name='Bottom')
    for field in top_region.fields:
        if (new_field := create_field_with_offset(field, BOTTOM_HALF_Y_OFFSET)) is not None:
            bottom_region.fields.append(new_field)
    new_form.regions[bottom_region.local_id] = bottom_region

    session.add(new_form)
    session.commit()

    # Copy the reference form into our working dir
    if not new_form.path.exists():
        reference_image = list(project_path.glob(f'**/{new_form.path.name}'))
        assert reference_image, 'Failed to locate the reference image'
        ref_image = reference_image[0]

        print(f'Copying {ref_image} -> {new_form.path}')
        new_form.path.parent.mkdir(exist_ok=True)
        shutil.copy(ref_image, new_form.path)
