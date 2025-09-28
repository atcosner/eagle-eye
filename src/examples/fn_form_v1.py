import logging
import shutil
from pathlib import Path
from sqlalchemy.orm import Session

from src.database.exporters.text_exporter import TextExporter
from src.database.fields.checkbox_field import CheckboxField
from src.database.fields.circled_field import CircledField
from src.database.fields.circled_option import CircledOption
from src.database.fields.field_group import FieldGroup
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

FORM_BLANK_IMAGE_PATH = Path(__file__).parent / 'fn_field_form_v1.png'
assert FORM_BLANK_IMAGE_PATH.exists(), f'Form blank reference image does not exist: {FORM_BLANK_IMAGE_PATH}'
# SPECIES_LIST_PATH = Path(__file__).parent / 'ku_orn_taxonomy_reference.csv'
# assert SPECIES_LIST_PATH.exists(), f'Species list does not exist: {SPECIES_LIST_PATH}'


def add_fn_form_v1(session: Session) -> None:
    form = ReferenceForm(
        name='KU Mammalogy - FN Form v1',
        path=LocalPaths.reference_forms_directory() / FORM_BLANK_IMAGE_PATH.name,
        alignment_method=FormAlignmentMethod.AUTOMATIC,
        alignment_mark_count=None,
        linking_method=FormLinkingMethod.PREVIOUS_IDENTIFIER,
    )

    # copy the reference form into our working dir
    if not form.path.exists():
        shutil.copy(FORM_BLANK_IMAGE_PATH, form.path)

    #
    # HEADER REGION
    #
    header_region = FormRegion(local_id=0, name='Header')
    form.regions[header_region.local_id] = header_region
    header_region.groups = [
        FieldGroup(
            name='',
            visual_region=None,
            fields=[
                FormField(
                    text_field=TextField(
                        name='Data entered by:',
                        visual_region=BoxBounds(x=0, y=0, width=0, height=0),
                        synthetic_only=True,
                    ),
                ),
            ],
        ),
        FieldGroup(
            name='',
            visual_region=None,
            fields=[
                FormField(
                    text_field=TextField(
                        name='Pseudo-Accession',
                        visual_region=BoxBounds(x=333, y=46, width=220, height=56),
                        text_validator=TextValidator(
                            text_regex=r'^[0-9]{4}-PA[0-9]{1,3}$',
                            error_tooltip='Pseudo-Accession must be in the format: <YYYY>-PA<NUMBER>',
                        ),
                    ),
                ),
            ],
        ),
        FieldGroup(
            name='',
            visual_region=None,
            fields=[
                FormField(
                    text_field=TextField(
                        name='KU:Mamm',
                        visual_region=BoxBounds(x=1035, y=60, width=242, height=42),
                        text_validator=TextValidator(
                            datatype=TextValidatorDatatype.INTEGER,
                            text_required=False,
                        ),
                    ),
                ),
            ],
        ),
        FieldGroup(
            name='',
            visual_region=None,
            fields=[
                FormField(
                    identifier=True,
                    identifier_regex=r'^FN(?P<id>[0-9]{6})$',
                    text_field=TextField(
                        name='FN Number',
                        visual_region=BoxBounds(x=1391, y=57, width=181, height=61),
                        text_validator=TextValidator(
                            text_regex=r'^FN[0-9]{6}$',
                            error_tooltip='FN Numbers must be exactly 6 digits',
                        ),
                    ),
                ),
            ],
        ),
    ]

    #
    # ID/AGENT REGION
    #
    id_region = FormRegion(local_id=1, name='ID/Agent')
    form.regions[id_region.local_id] = id_region
    id_region.groups = [
        FieldGroup(
            name='',
            visual_region=None,
            fields=[
                FormField(
                    text_field=TextField(
                        name='Species',
                        visual_region=BoxBounds(x=319, y=169, width=511, height=45),
                        # text_validator=TextValidator(
                        #     datatype=TextValidatorDatatype.LIST_CHOICE,
                        #     allow_closest_match_correction=True,
                        #     text_choices=[TextChoice(text=t) for t in species_list], TODO: Add mammalogy species csv
                        # ),
                    ),
                ),
            ],
        ),
        FieldGroup(
            name='',
            visual_region=None,
            fields=[
                FormField(
                    text_field=TextField(
                        name='ID by',
                        visual_region=BoxBounds(x=908, y=168, width=210, height=46),
                        # text_validator=TextValidator(
                        #     datatype=TextValidatorDatatype.LIST_CHOICE,
                        #     allow_closest_match_correction=True,
                        #     text_choices=[TextChoice(text=t) for t in agent_list], TODO: Add mammalogy agent csv
                        # ),
                    ),
                ),
            ],
        ),
        FieldGroup(
            name='',
            visual_region=None,
            fields=[
                FormField(
                    multi_checkbox_field=MultiCheckboxField(
                        name='ID confidence',
                        visual_region=BoxBounds(x=1122, y=176, width=457, height=47),
                        validator=MultiCheckboxValidation.REQUIRE_ONE,
                        checkboxes=[
                            MultiCheckboxOption(name='Low', region=BoxBounds(x=1324, y=193, width=12, height=14)),
                            MultiCheckboxOption(name='Medium', region=BoxBounds(x=1405, y=193, width=12, height=14)),
                            MultiCheckboxOption(name='High', region=BoxBounds(x=1499, y=193, width=12, height=14)),
                        ],
                    )
                ),
            ],
        ),
        FieldGroup(
            name='',
            visual_region=None,
            fields=[
                FormField(
                    text_field=TextField(
                        name='GPS Waypoint ID',
                        visual_region=BoxBounds(x=438, y=220, width=249, height=45),
                        text_validator=TextValidator(
                            text_regex=r'^[A-Z]{3,4}[0-9]{1,3}$',
                            error_tooltip='GPS Waypoint ID must be 3-4 letters followed by 1-3 numbers',
                        ),
                    ),
                ),
            ],
        ),
        FieldGroup(
            name='',
            visual_region=None,
            fields=[
                FormField(
                    text_field=TextField(
                        name='Trapline ID',
                        visual_region=BoxBounds(x=838, y=224, width=247, height=41),
                    ),
                ),
            ],
        ),
        FieldGroup(
            name='',
            visual_region=None,
            fields=[
                FormField(
                    text_field=TextField(
                        name='BlueCard/Other #',
                        visual_region=BoxBounds(x=1312, y=224, width=263, height=41),
                    ),
                ),
            ],
        ),

        FieldGroup(
            name='',
            visual_region=None,
            fields=[
                FormField(
                    text_field=TextField(
                        name='Collector(s), Coll #',
                        visual_region=BoxBounds(x=443, y=278, width=698, height=45),
                        # text_validator=TextValidator(
                        #     datatype=TextValidatorDatatype.LIST_CHOICE,
                        #     allow_closest_match_correction=True,
                        #     text_choices=[TextChoice(text=t) for t in agent_list], TODO: Add mammalogy agent csv
                        # ),
                    ),
                ),
            ],
        ),
        FieldGroup(
            name='',
            visual_region=None,
            fields=[
                FormField(
                    text_field=TextField(
                        name='Collection Date',
                        visual_region=BoxBounds(x=1269, y=282, width=314, height=41),
                        text_validator=TextValidator(
                            datatype=TextValidatorDatatype.DATE,
                        ),
                    ),
                ),
            ],
        ),

        FieldGroup(
            name='',
            visual_region=None,
            fields=[
                FormField(
                    text_field=TextField(
                        name='Preparator, Prep #',
                        visual_region=BoxBounds(x=440, y=337, width=226, height=46),
                        # text_validator=TextValidator(
                        #     datatype=TextValidatorDatatype.LIST_CHOICE,
                        #     allow_closest_match_correction=True,
                        #     text_choices=[TextChoice(text=t) for t in agent_list], TODO: Add mammalogy agent csv
                        # ),
                    ),
                ),
            ],
        ),
        FieldGroup(
            name='',
            visual_region=None,
            fields=[
                FormField(
                    text_field=TextField(
                        name='Prep Date',
                        visual_region=BoxBounds(x=802, y=337, width=226, height=46),
                        text_validator=TextValidator(
                            datatype=TextValidatorDatatype.DATE,
                        ),
                    ),
                ),
            ],
        ),
        FieldGroup(
            name='',
            visual_region=None,
            fields=[
                FormField(
                    text_field=TextField(
                        name='Tissue by, Date',
                        visual_region=BoxBounds(x=1238, y=351, width=344, height=32),
                        # TODO: this should probably have a custom validator since it's a composite field
                    ),
                ),
            ],
        ),
    ]

    #
    # LOCALITY REGION
    #
    locality_region = FormRegion(local_id=2, name='Locality')
    form.regions[locality_region.local_id] = locality_region
    locality_region.groups = [
        FieldGroup(
            name='',
            visual_region=None,
            fields=[
                FormField(
                    text_field=TextField(
                        name='Country/State',
                        visual_region=BoxBounds(x=392, y=422, width=620, height=45),
                        # text_validator=TextValidator( TODO: probably want a custom validator since there can be multiple formats
                        #     datatype=TextValidatorDatatype.DATE,
                        # ),
                    ),
                ),
            ],
        ),
        FieldGroup(
            name='',
            visual_region=None,
            fields=[
                FormField(
                    text_field=TextField(
                        name='County',
                        visual_region=BoxBounds(x=1113, y=424, width=461, height=43),
                        # text_validator=TextValidator(
                        #     datatype=TextValidatorDatatype.LIST_CHOICE,
                        #     allow_closest_match_correction=True,
                        #     text_choices=[TextChoice(text=t) for t in agent_list], TODO: add county CSV or use internet?
                        # ),
                    ),
                ),
            ],
        ),
        FieldGroup(
            name='',
            visual_region=None,
            fields=[
                FormField(
                    text_field=TextField(
                        name='Locality',
                        visual_region=BoxBounds(x=316, y=472, width=1264, height=43),
                    ),
                ),
            ],
        ),

        FieldGroup(
            name='',
            visual_region=None,
            fields=[
                FormField(
                    text_field=TextField(
                        name='Latitude',
                        visual_region=BoxBounds(x=261, y=521, width=431, height=42),
                        text_validator=TextValidator(
                            datatype=TextValidatorDatatype.GPS_POINT_DD,
                            text_required=False,
                        ),
                    ),
                ),
            ],
        ),
        FieldGroup(
            name='',
            visual_region=None,
            fields=[
                FormField(
                    text_field=TextField(
                        name='Longitude',
                        visual_region=BoxBounds(x=772, y=521, width=434, height=42),
                        text_validator=TextValidator(
                            datatype=TextValidatorDatatype.GPS_POINT_DD,
                            text_required=False,
                        ),
                    ),
                ),
            ],
        ),
        FieldGroup(
            name='',
            visual_region=None,
            fields=[
                FormField(
                    text_field=TextField(
                        name='Altitude',
                        visual_region=BoxBounds(x=1367, y=521, width=213, height=42),
                        text_validator=TextValidator(
                            datatype=TextValidatorDatatype.INTEGER,
                            text_required=False,
                        ),
                    ),
                ),
            ],
        ),

        FieldGroup(
            name='',
            visual_region=None,
            fields=[
                FormField(
                    text_field=TextField(
                        name='Error (m)',
                        visual_region=BoxBounds(x=335, y=570, width=335, height=45),
                        text_validator=TextValidator(
                            datatype=TextValidatorDatatype.INTEGER,
                            text_required=False,
                        ),
                    ),
                ),
            ],
        ),
        FieldGroup(
            name='',
            visual_region=None,
            fields=[
                FormField(
                    text_field=TextField(
                        name='Source',
                        visual_region=BoxBounds(x=776, y=572, width=307, height=46),
                        text_validator=TextValidator(
                            datatype=TextValidatorDatatype.LIST_CHOICE,
                            allow_closest_match_correction=True,
                            text_choices=[
                                TextChoice('GPS unit'),
                                TextChoice('GeoLocate'),
                                TextChoice('Google Earth'),
                                TextChoice('Google Maps'),
                                TextChoice('Map Centroid'),
                            ],
                        ),
                    ),
                ),
            ],
        ),
        FieldGroup(
            name='',
            visual_region=None,
            fields=[
                FormField(
                    text_field=TextField(
                        name='Locality same as FN',
                        visual_region=BoxBounds(x=1343, y=575, width=232, height=41),
                        text_validator=TextValidator(
                            text_regex=r'^[0-9]{6}$',
                            error_tooltip='FN Numbers must be exactly 6 digits',
                        ),
                    ),
                ),
            ],
        ),
    ]

    #
    # ATTRIBUTES REGION
    #
    attributes_region = FormRegion(local_id=3, name='Attributes')
    form.regions[attributes_region.local_id] = attributes_region
    attributes_region.groups = [
        FieldGroup(
            name='Measurements',
            visual_region=BoxBounds(x=405, y=638, width=1089, height=79),
            fields=[
                FormField(
                    text_field=TextField(
                        name='Total (mm)',
                        visual_region=BoxBounds(x=408, y=639, width=104, height=45),
                        text_validator=TextValidator(
                            datatype=TextValidatorDatatype.INTEGER,
                        ),
                    ),
                ),
                FormField(
                    text_field=TextField(
                        name='Tail (mm)',
                        visual_region=BoxBounds(x=516, y=638, width=103, height=46),
                        text_validator=TextValidator(
                            datatype=TextValidatorDatatype.INTEGER,
                        ),
                    ),
                ),
                FormField(
                    text_field=TextField(
                        name='Hindfoot (mm)',
                        visual_region=BoxBounds(x=622, y=637, width=100, height=47),
                        text_validator=TextValidator(
                            datatype=TextValidatorDatatype.INTEGER,
                        ),
                    ),
                ),
                FormField(
                    text_field=TextField(
                        name='Ear (mm)',
                        visual_region=BoxBounds(x=723, y=637, width=104, height=47),
                        text_validator=TextValidator(
                            datatype=TextValidatorDatatype.INTEGER,
                        ),
                    ),
                ),
                FormField(
                    text_field=TextField(
                        name='Weight (g)',
                        visual_region=BoxBounds(x=830, y=637, width=104, height=47),
                        text_validator=TextValidator(
                            datatype=TextValidatorDatatype.INTEGER,
                        ),
                    ),
                ),
                FormField(
                    text_field=TextField(
                        name='Measured by',
                        visual_region=BoxBounds(x=955, y=637, width=226, height=47),
                    ),
                ),
                FormField(
                    text_field=TextField(
                        name='Bats: forearm (mm)',
                        visual_region=BoxBounds(x=1264, y=638, width=108, height=46),
                        text_validator=TextValidator(
                            datatype=TextValidatorDatatype.INTEGER,
                            text_required=False,
                        ),
                    ),
                ),
                FormField(
                    text_field=TextField(
                        name='Bats: tragus (mm)',
                        visual_region=BoxBounds(x=1375, y=638, width=110, height=46),
                        text_validator=TextValidator(
                            datatype=TextValidatorDatatype.INTEGER,
                            text_required=False,
                        ),
                    ),
                ),
            ],
        ),
        FieldGroup(
            name='',
            visual_region=None,
            fields=[
                FormField(
                    multi_checkbox_field=MultiCheckboxField(
                        name='Age Class',
                        visual_region=BoxBounds(x=207, y=730, width=573, height=44),
                        validator=MultiCheckboxValidation.REQUIRE_ONE,
                        checkboxes=[
                            MultiCheckboxOption(name='Adult', region=BoxBounds(x=346, y=746, width=11, height=12)),
                            MultiCheckboxOption(name='Subadult', region=BoxBounds(x=447, y=746, width=11, height=12)),
                            MultiCheckboxOption(name='Juvenile', region=BoxBounds(x=534, y=746, width=11, height=12)),
                            MultiCheckboxOption(name='Embryo', region=BoxBounds(x=616, y=746, width=11, height=12)),
                            MultiCheckboxOption(name='Unknown', region=BoxBounds(x=711, y=746, width=11, height=12)),
                        ],
                    )
                ),
            ],
        ),
        FieldGroup(
            name='Relationship',
            visual_region=BoxBounds(x=896, y=725, width=685, height=54),
            fields=[
                FormField(
                    text_field=TextField(
                        name='Type',
                        visual_region=BoxBounds(x=1062, y=731, width=256, height=34),
                    ),
                ),
                FormField(
                    text_field=TextField(
                        name='Other ID',
                        visual_region=BoxBounds(x=1365, y=728, width=206, height=37),
                    ),
                ),
            ],
        ),
        FieldGroup(
            name='Male',
            visual_region=BoxBounds(x=200, y=792, width=927, height=48),
            fields=[
                FormField(
                    checkbox_field=CheckboxField(
                        name='Is Male?',
                        visual_region=BoxBounds(x=205, y=791, width=128, height=41),
                        checkbox_region=BoxBounds(x=216, y=806, width=11, height=12),
                    ),
                ),
                FormField(
                    multi_checkbox_field=MultiCheckboxField(
                        name='External',
                        visual_region=BoxBounds(x=353, y=793, width=421, height=36),
                        validator=MultiCheckboxValidation.REQUIRE_ONE,
                        checkboxes=[
                            MultiCheckboxOption(name='Scrotal', region=BoxBounds(x=483, y=806, width=11, height=12)),
                            MultiCheckboxOption(name='Non-scrotal', region=BoxBounds(x=617, y=806, width=11, height=12)),
                        ],
                    )
                ),
                FormField(
                    text_field=TextField(
                        name='Testes',
                        visual_region=BoxBounds(x=801, y=793, width=311, height=43),
                        text_regions=[
                            BoxBounds(x=909, y=796, width=73, height=28),
                            BoxBounds(x=995, y=795, width=69, height=29),
                        ],
                    ),
                ),
            ],
        ),
        FieldGroup(
            name='Female',
            visual_region=BoxBounds(x=199, y=841, width=1384, height=98),
            fields=[
                FormField(
                    checkbox_field=CheckboxField(
                        name='Is Female?',
                        visual_region=BoxBounds(x=202, y=843, width=152, height=50),
                        checkbox_region=BoxBounds(x=216, y=861, width=11, height=12),
                    ),
                ),
                FormField(
                    multi_checkbox_field=MultiCheckboxField(
                        name='Vagina',
                        visual_region=BoxBounds(x=350, y=846, width=348, height=42),
                        validator=MultiCheckboxValidation.NONE,
                        checkboxes=[
                            MultiCheckboxOption(name='Open', region=BoxBounds(x=466, y=861, width=11, height=12)),
                            MultiCheckboxOption(name='Closed', region=BoxBounds(x=584, y=861, width=11, height=12)),
                        ],
                    )
                ),
                FormField(
                    multi_checkbox_field=MultiCheckboxField(
                        name='Mammae',
                        visual_region=BoxBounds(x=720, y=847, width=382, height=40),
                        validator=MultiCheckboxValidation.NONE,
                        checkboxes=[
                            MultiCheckboxOption(name='Enlarged', region=BoxBounds(x=858, y=861, width=11, height=12)),
                            MultiCheckboxOption(name='Small', region=BoxBounds(x=1014, y=861, width=11, height=12)),
                        ],
                    )
                ),
                FormField(
                    multi_checkbox_field=MultiCheckboxField(
                        name='Lactation',
                        visual_region=BoxBounds(x=1139, y=852, width=443, height=33),
                        validator=MultiCheckboxValidation.NONE,
                        checkboxes=[
                            MultiCheckboxOption(name='Lactating', region=BoxBounds(x=1270, y=861, width=11, height=12)),
                            MultiCheckboxOption(name='Not Lactating', region=BoxBounds(x=1421, y=861, width=11, height=12)),
                        ],
                    )
                ),
                #
                # TODO: Placental scars, embryo
                #
            ],
        ),
        FieldGroup(
            name='',
            visual_region=None,
            fields=[
                FormField(
                    checkbox_field=CheckboxField(
                        name='Sex Unknown',
                        visual_region=BoxBounds(x=201, y=944, width=195, height=40),
                        checkbox_region=BoxBounds(x=216, y=958, width=11, height=12),
                    )
                ),
            ],
        ),
        FieldGroup(
            name='',
            visual_region=None,
            fields=[
                FormField(
                    checkbox_field=CheckboxField(
                        name='Sex Not Examined',
                        visual_region=BoxBounds(x=417, y=944, width=241, height=40),
                        checkbox_region=BoxBounds(x=429, y=958, width=11, height=12),
                    )
                ),
            ],
        ),
        FieldGroup(
            name='Ecto Parasites',
            visual_region=BoxBounds(x=199, y=989, width=1376, height=50),
            fields=[
                FormField(
                    circled_field=CircledField(
                        name='Exam?',
                        visual_region=BoxBounds(x=204, y=992, width=248, height=41),
                        options=[
                            CircledOption(name='Yes', region=BoxBounds(x=354, y=994, width=39, height=38)),
                            CircledOption(name='No', region=BoxBounds(x=404, y=992, width=41, height=40)),
                        ],
                    )
                ),
                FormField(
                    circled_field=CircledField(
                        name='Found?',
                        visual_region=BoxBounds(x=446, y=991, width=262, height=41),
                        options=[
                            CircledOption(name='Yes', region=BoxBounds(x=603, y=992, width=41, height=40)),
                            CircledOption(name='No', region=BoxBounds(x=658, y=990, width=40, height=42)),
                        ],
                    )
                ),
                FormField(
                    text_field=TextField(
                        name='By',
                        visual_region=BoxBounds(x=753, y=992, width=150, height=33),
                    ),
                ),
                FormField(
                    text_field=TextField(
                        name='Date',
                        visual_region=BoxBounds(x=965, y=990, width=149, height=35),
                        text_validator=TextValidator(
                            datatype=TextValidatorDatatype.DATE,
                        ),
                    ),
                ),
                FormField(
                    text_field=TextField(
                        name='Method',
                        visual_region=BoxBounds(x=1208, y=986, width=368, height=39),
                    ),
                ),
            ],
        ),
        FieldGroup(
            name='Endo Parasites',
            visual_region=BoxBounds(x=204, y=1037, width=1373, height=47),
            fields=[
                FormField(
                    circled_field=CircledField(
                        name='Exam?',
                        visual_region=BoxBounds(x=206, y=1042, width=247, height=40),
                        options=[
                            CircledOption(name='Yes', region=BoxBounds(x=358, y=1043, width=44, height=39)),
                            CircledOption(name='No', region=BoxBounds(x=413, y=1040, width=40, height=44)),
                        ],
                    )
                ),
                FormField(
                    circled_field=CircledField(
                        name='Found?',
                        visual_region=BoxBounds(x=453, y=1039, width=248, height=45),
                        options=[
                            CircledOption(name='Yes', region=BoxBounds(x=608, y=1041, width=39, height=42)),
                            CircledOption(name='No', region=BoxBounds(x=659, y=1044, width=43, height=40)),
                        ],
                    )
                ),
                FormField(
                    text_field=TextField(
                        name='By',
                        visual_region=BoxBounds(x=753, y=1037, width=154, height=38),
                    ),
                ),
                FormField(
                    text_field=TextField(
                        name='Date',
                        visual_region=BoxBounds(x=967, y=1039, width=149, height=36),
                        text_validator=TextValidator(
                            datatype=TextValidatorDatatype.DATE,
                            text_required=False,
                        ),
                    ),
                ),
                FormField(
                    text_field=TextField(
                        name='Method',
                        visual_region=BoxBounds(x=1210, y=1039, width=362, height=36),
                    ),
                ),
            ],
        ),
    ]

    #
    # PREP REGION
    #
    parts_region = FormRegion(local_id=4, name='Preparations/Parts')
    form.regions[parts_region.local_id] = parts_region
    parts_region.groups = [
        FieldGroup(
            name='',
            visual_region=None,
            fields=[
                FormField(
                    circled_field=CircledField(
                        name='DOA',
                        visual_region=BoxBounds(x=1415, y=1161, width=170, height=54),
                        options=[
                            CircledOption(name='Y', region=BoxBounds(x=1496, y=1173, width=33, height=33)),
                            CircledOption(name='N', region=BoxBounds(x=1540, y=1172, width=33, height=33)),
                        ],
                    )
                ),
            ],
        ),
    ]

    #
    # FOOTER REGION
    #
    footer_region = FormRegion(local_id=5, name='Footer')
    form.regions[footer_region.local_id] = footer_region
    footer_region.groups = [
        FieldGroup(
            name='',
            visual_region=None,
            fields=[
                FormField(
                    text_field=TextField(
                        name='Remarks',
                        visual_region=BoxBounds(x=190, y=1931, width=1400, height=137),
                        text_regions=[
                            BoxBounds(x=551, y=1934, width=1030, height=35),
                            BoxBounds(x=195, y=1971, width=1383, height=41),
                            BoxBounds(x=192, y=2017, width=1390, height=39),
                        ],
                    )
                ),
            ],
        ),
    ]

    session.add(form)
    session.commit()
