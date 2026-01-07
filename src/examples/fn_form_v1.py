import logging
import shutil
from pathlib import Path
from sqlalchemy.orm import Session

from src.database.exporters.multi_checkbox_exporter import MultiCheckboxExporter
from src.database.exporters.text_exporter import TextExporter
from src.database.fields.checkbox_field import CheckboxField
from src.database.fields.circled_field import CircledField
from src.database.fields.circled_option import CircledOption
from src.database.fields.field_group import FieldGroup
from src.database.fields.form_field import FormField
from src.database.fields.multi_checkbox_field import MultiCheckboxField
from src.database.fields.multi_checkbox_option import MultiCheckboxOption
from src.database.fields.sub_circled_option import SubCircledOption
from src.database.fields.text_field import TextField
from src.database.form_region import FormRegion
from src.database.reference_form import ReferenceForm
from src.database.validation.custom_data import CustomData
from src.database.validation.text_choice import TextChoice
from src.database.validation.text_validator import TextValidator
from src.util.export import MultiCbExportType
from src.util.paths import LocalPaths
from src.util.types import BoxBounds, FormLinkingMethod, FormAlignmentMethod
from src.util.validation import MultiChoiceValidation, TextValidatorDatatype

logger = logging.getLogger(__name__)

FORM_BLANK_IMAGE_PATH = Path(__file__).parent / 'fn_field_form_v1.png'
assert FORM_BLANK_IMAGE_PATH.exists(), f'Form blank reference image does not exist: {FORM_BLANK_IMAGE_PATH}'
AGENT_LIST_PATH = Path(__file__).parent / 'data' / 'fn_agent_master.csv'
assert AGENT_LIST_PATH.exists(), f'Agent list does not exist: {AGENT_LIST_PATH}'
COUNTRY_LIST_PATH = Path(__file__).parent / 'data' / 'fn_country_master.csv'
assert COUNTRY_LIST_PATH.exists(), f'Country list does not exist: {COUNTRY_LIST_PATH}'
COUNTY_LIST_PATH = Path(__file__).parent / 'data' / 'fn_county_master.csv'
assert COUNTY_LIST_PATH.exists(), f'County list does not exist: {COUNTY_LIST_PATH}'
SPECIES_LIST_PATH = Path(__file__).parent / 'data' / 'fn_mammal_diversity_database.csv'
assert SPECIES_LIST_PATH.exists(), f'Species list does not exist: {SPECIES_LIST_PATH}'
STATE_LIST_PATH = Path(__file__).parent / 'data' / 'fn_state_master.csv'
assert STATE_LIST_PATH.exists(), f'State list does not exist: {STATE_LIST_PATH}'


def _read_csv(path: Path) -> list[str]:
    with path.open('r') as file:
        return sorted({line.strip() for line in file.readlines()})


def _read_species_list() -> list[str]:
    with SPECIES_LIST_PATH.open('r') as file:
        return sorted({line.strip().lower().replace('_', ' ') for line in file.readlines()})


def add_fn_form_v1(session: Session) -> None:
    # read in the controlled vocabulary datasets
    agent_list = _read_csv(AGENT_LIST_PATH)
    county_list = _read_csv(COUNTY_LIST_PATH)
    country_list = _read_csv(COUNTRY_LIST_PATH)
    species_list = _read_species_list()
    state_list = _read_csv(STATE_LIST_PATH)

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
                        text_exporter=TextExporter(
                            export_field_name='entered_by',
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
                        name='Pseudo-Accession',
                        visual_region=BoxBounds(x=333, y=46, width=220, height=56),
                        text_validator=TextValidator(
                            text_regex=r'^[0-9]{4}-PA[0-9]{1,3}$',
                            error_tooltip='Pseudo-Accession must be in the format: <YYYY>-PA<NUMBER>',
                        ),
                        text_exporter=TextExporter(
                            export_field_name='pseudo-accn',
                            capitalize=True,
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
                        text_exporter=TextExporter(
                            export_field_name='catalog#',
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
                        text_exporter=TextExporter(
                            export_field_name='FN#',
                            capitalize=True,
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
                        text_validator=TextValidator(
                            datatype=TextValidatorDatatype.LIST_CHOICE,
                            allow_closest_match_correction=True,
                            text_choices=[TextChoice(text=t) for t in species_list],
                        ),
                        # TODO: export capitalization?
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
                        text_validator=TextValidator(
                            datatype=TextValidatorDatatype.LIST_CHOICE,
                            allow_closest_match_correction=True,
                            text_choices=[TextChoice(text=t) for t in agent_list],
                        ),
                        text_exporter=TextExporter(
                            export_field_name='ID_by',
                            capitalize=True,
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
                        name='ID confidence',
                        visual_region=BoxBounds(x=1122, y=176, width=457, height=47),
                        validator=MultiChoiceValidation.REQUIRE_ONE,
                        checkboxes=[
                            MultiCheckboxOption(name='Low', region=BoxBounds(x=1324, y=193, width=12, height=14)),
                            MultiCheckboxOption(name='Medium', region=BoxBounds(x=1405, y=193, width=12, height=14)),
                            MultiCheckboxOption(name='High', region=BoxBounds(x=1499, y=193, width=12, height=14)),
                        ],
                        exporter=MultiCheckboxExporter(
                            export_field_name='ID_confidence',
                            export_type=MultiCbExportType.SINGLE_COLUMN,
                        ),
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
                        text_exporter=TextExporter(
                            export_field_name='GPS_waypoint_ID',
                            capitalize=True,
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
                        text_exporter=TextExporter(
                            export_field_name='trapline_ID',
                            capitalize=True,
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
                        name='BlueCard/Other #',
                        visual_region=BoxBounds(x=1312, y=224, width=263, height=41),
                        text_exporter=TextExporter(
                            export_field_name='BlueCard_other#',
                            capitalize=True,
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
                        name='Collector(s), Coll #',
                        visual_region=BoxBounds(x=443, y=278, width=698, height=45),
                        text_validator=TextValidator(
                            datatype=TextValidatorDatatype.CSV_OF_CHOICE,
                            allow_closest_match_correction=True,
                            text_choices=[TextChoice(text=t) for t in agent_list],
                        ),
                        # TODO: validation
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
                        text_validator=TextValidator(
                            datatype=TextValidatorDatatype.LIST_CHOICE,
                            allow_closest_match_correction=True,
                            text_choices=[TextChoice(text=t) for t in agent_list],
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
            name='Tissue By',
            visual_region=BoxBounds(x=1238, y=342, width=340, height=41),
            fields=[
                FormField(
                    text_field=TextField(
                        name='Initials',
                        visual_region=BoxBounds(x=1231, y=331, width=106, height=52),
                        text_validator=TextValidator(
                            datatype=TextValidatorDatatype.LIST_CHOICE,
                            allow_closest_match_correction=True,
                            text_choices=[TextChoice(text=t) for t in agent_list],
                        ),
                    ),
                ),
                FormField(
                    text_field=TextField(
                        name='Date',
                        visual_region=BoxBounds(x=1341, y=341, width=234, height=43),
                        text_validator=TextValidator(
                            datatype=TextValidatorDatatype.DATE,
                        ),
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
                        text_validator=TextValidator(
                            datatype=TextValidatorDatatype.FN_COUNTRY_STATE,
                            text_regex=r"([a-zA-Z ]*)\/([a-zA-Z ]*)",
                            custom_data={
                                0: CustomData(key=0, text_choices=[TextChoice(text=t) for t in country_list]),
                                1: CustomData(key=1, text_choices=[TextChoice(text=t) for t in state_list]),
                            },
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
                        name='County',
                        visual_region=BoxBounds(x=1113, y=424, width=461, height=43),
                        text_validator=TextValidator(
                            datatype=TextValidatorDatatype.LIST_CHOICE,
                            allow_closest_match_correction=True,
                            text_choices=[TextChoice(text=t) for t in county_list],
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
                        name='Altitude (m)',
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
                            text_regex=r'^FN[0-9]{6}$',
                            error_tooltip='FN Numbers must be exactly 6 digits',
                            text_required=False,
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
                        text_validator=TextValidator(
                            datatype=TextValidatorDatatype.LIST_CHOICE,
                            allow_closest_match_correction=True,
                            text_choices=[TextChoice(text=t) for t in agent_list],
                        ),
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
                        validator=MultiChoiceValidation.REQUIRE_ONE,
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
                        text_validator=TextValidator(
                            datatype=TextValidatorDatatype.LIST_CHOICE,
                            allow_closest_match_correction=True,
                            text_choices=[
                                TextChoice('self'),
                                TextChoice('littermate of'),
                                TextChoice('mate of'),
                                TextChoice('sibling of'),
                                TextChoice('parasite of'),
                                TextChoice('host of'),
                                TextChoice('ate'),
                                TextChoice('eaten by'),
                                TextChoice('offspring of'),
                                TextChoice('mother or parent of'),
                                TextChoice('mounted with'),
                                TextChoice('symbiont of'),
                                TextChoice('host of symbiont'),
                            ],
                        ),
                    ),
                ),
                FormField(
                    text_field=TextField(
                        name='Other ID',
                        visual_region=BoxBounds(x=1365, y=728, width=206, height=37),
                        text_validator=TextValidator(
                            text_regex=r'^FN[0-9]{6}$',
                            error_tooltip='FN Numbers must be exactly 6 digits',
                        ),
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
                        validator=MultiChoiceValidation.REQUIRE_ONE,
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
                        validator=MultiChoiceValidation.NONE,
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
                        validator=MultiChoiceValidation.NONE,
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
                        validator=MultiChoiceValidation.NONE,
                        checkboxes=[
                            MultiCheckboxOption(name='Lactating', region=BoxBounds(x=1270, y=861, width=11, height=12)),
                            MultiCheckboxOption(name='Not Lactating', region=BoxBounds(x=1421, y=861, width=11, height=12)),
                        ],
                    )
                ),
                FormField(
                    circled_field=CircledField(
                        name='Placental Scars',
                        visual_region=BoxBounds(x=606, y=883, width=111, height=57),
                        validator=MultiChoiceValidation.MAXIMUM_ONE,
                        options=[
                            CircledOption(name='Yes', region=BoxBounds(x=610, y=887, width=47, height=45)),
                            CircledOption(name='No', region=BoxBounds(x=668, y=888, width=43, height=46)),
                        ],
                    )
                ),
                FormField(
                    text_field=TextField(
                        name='Plsc - Right',
                        visual_region=BoxBounds(x=726, y=888, width=56, height=36),
                        text_validator=TextValidator(
                            datatype=TextValidatorDatatype.INTEGER,
                            text_required=False,
                        ),
                    )
                ),
                FormField(
                    text_field=TextField(
                        name='Plsc - Left',
                        visual_region=BoxBounds(x=808, y=886, width=62, height=38),
                        text_validator=TextValidator(
                            datatype=TextValidatorDatatype.INTEGER,
                            text_required=False,
                        ),
                    )
                ),
                FormField(
                    circled_field=CircledField(
                        name='Embryo',
                        visual_region=BoxBounds(x=1040, y=882, width=109, height=58),
                        validator=MultiChoiceValidation.MAXIMUM_ONE,
                        options=[
                            CircledOption(name='Yes', region=BoxBounds(x=1045, y=890, width=46, height=44)),
                            CircledOption(name='No', region=BoxBounds(x=1099, y=889, width=46, height=45)),
                        ],
                    )
                ),
                FormField(
                    text_field=TextField(
                        name='Embryo - Right',
                        visual_region=BoxBounds(x=1158, y=887, width=58, height=37),
                        text_validator=TextValidator(
                            datatype=TextValidatorDatatype.INTEGER,
                            text_required=False,
                        ),
                    )
                ),
                FormField(
                    text_field=TextField(
                        name='Embryo - Left',
                        visual_region=BoxBounds(x=1242, y=885, width=61, height=39),
                        text_validator=TextValidator(
                            datatype=TextValidatorDatatype.INTEGER,
                            text_required=False,
                        ),
                    )
                ),
                FormField(
                    text_field=TextField(
                        name='Embryo - CR',
                        visual_region=BoxBounds(x=1389, y=886, width=85, height=38),
                        text_validator=TextValidator(
                            datatype=TextValidatorDatatype.INTEGER,
                            text_required=False,
                        ),
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
                        validator=MultiChoiceValidation.MAXIMUM_ONE,
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
                        validator=MultiChoiceValidation.MAXIMUM_ONE,
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
                        text_validator=TextValidator(
                            datatype=TextValidatorDatatype.LIST_CHOICE,
                            allow_closest_match_correction=True,
                            text_choices=[TextChoice(text=t) for t in agent_list],
                        ),
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
                        validator=MultiChoiceValidation.MAXIMUM_ONE,
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
                        validator=MultiChoiceValidation.MAXIMUM_ONE,
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
                        text_validator=TextValidator(
                            datatype=TextValidatorDatatype.LIST_CHOICE,
                            allow_closest_match_correction=True,
                            text_choices=[TextChoice(text=t) for t in agent_list],
                        ),
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
                    multi_checkbox_field=MultiCheckboxField(
                        name='Prep Types',
                        visual_region=BoxBounds(x=382, y=1101, width=1200, height=61),
                        validator=MultiChoiceValidation.REQUIRE_ONE,
                        checkboxes=[
                            MultiCheckboxOption(name='Skin', region=BoxBounds(x=410, y=1128, width=12, height=12)),
                            MultiCheckboxOption(name='Skull', region=BoxBounds(x=509, y=1128, width=12, height=12)),
                            MultiCheckboxOption(name='Skull + Skel', region=BoxBounds(x=621, y=1128, width=12, height=12)),
                            MultiCheckboxOption(
                                name='Whole Org',
                                region=BoxBounds(x=804, y=1128, width=12, height=12),
                                circled_options=[
                                    SubCircledOption(name='95% EtOH', region=BoxBounds(x=956, y=1100, width=71, height=58)),
                                    SubCircledOption(name='Frozen', region=BoxBounds(x=1039, y=1106, width=54, height=57)),
                                ]
                            ),
                            MultiCheckboxOption(name='Tissue only', region=BoxBounds(x=1125, y=1128, width=12, height=12)),
                            MultiCheckboxOption(
                                name='Other',
                                region=BoxBounds(x=1320, y=1128, width=12, height=12),
                                text_region=BoxBounds(x=1415, y=1103, width=158, height=43),
                            ),
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
                    multi_checkbox_field=MultiCheckboxField(
                        name='Collection Method',
                        visual_region=BoxBounds(x=270, y=1163, width=1150, height=52),
                        validator=MultiChoiceValidation.REQUIRE_ONE,
                        checkboxes=[
                            MultiCheckboxOption(name='Sherman', region=BoxBounds(x=285, y=1183, width=12, height=12)),
                            MultiCheckboxOption(name='Snap', region=BoxBounds(x=409, y=1183, width=12, height=12)),
                            MultiCheckboxOption(name='Rat', region=BoxBounds(x=510, y=1183, width=12, height=12)),
                            MultiCheckboxOption(name='Gopher', region=BoxBounds(x=592, y=1183, width=12, height=12)),
                            MultiCheckboxOption(name='Pit', region=BoxBounds(x=691, y=1183, width=12, height=12)),
                            MultiCheckboxOption(name='Net', region=BoxBounds(x=763, y=1183, width=12, height=12)),
                            MultiCheckboxOption(name='Gun', region=BoxBounds(x=845, y=1183, width=12, height=12)),
                            MultiCheckboxOption(name='Salvage', region=BoxBounds(x=935, y=1183, width=12, height=12)),
                            MultiCheckboxOption(name='Tomahawk', region=BoxBounds(x=1068, y=1183, width=12, height=12)),
                            MultiCheckboxOption(
                                name='Other',
                                region=BoxBounds(x=1182, y=1183, width=12, height=12),
                                text_region=BoxBounds(x=1265, y=1159, width=144, height=42),
                            ),
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
                    circled_field=CircledField(
                        name='DOA',
                        visual_region=BoxBounds(x=1415, y=1161, width=170, height=54),
                        validator=MultiChoiceValidation.REQUIRE_ONE,
                        options=[
                            CircledOption(name='Y', region=BoxBounds(x=1496, y=1173, width=33, height=33)),
                            CircledOption(name='N', region=BoxBounds(x=1540, y=1172, width=33, height=33)),
                        ],
                    )
                ),
            ],
        ),
        FieldGroup(
            name='Heart, Lung',
            visual_region=BoxBounds(x=195, y=1301, width=606, height=66),
            fields=[
                FormField(
                    multi_checkbox_field=MultiCheckboxField(
                        name='Preserved',
                        visual_region=BoxBounds(x=324, y=1301, width=188, height=66),
                        validator=MultiChoiceValidation.OPTIONAL,
                        checkboxes=[
                            MultiCheckboxOption(name='-20 C', region=BoxBounds(x=333, y=1314, width=12, height=12)),
                            MultiCheckboxOption(name='-80 C', region=BoxBounds(x=333, y=1347, width=12, height=12)),
                            MultiCheckboxOption(name='LN2', region=BoxBounds(x=424, y=1314, width=12, height=12)),
                            MultiCheckboxOption(name='Shield', region=BoxBounds(x=424, y=1347, width=12, height=12)),
                        ],
                    )
                ),
                FormField(
                    text_field=TextField(
                        name='Remarks',
                        visual_region=BoxBounds(x=627, y=1301, width=175, height=66),
                    ),
                ),
            ],
        ),
        FieldGroup(
            name='Kidney, Spleen',
            visual_region=BoxBounds(x=195, y=1371, width=606, height=66),
            fields=[
                FormField(
                    multi_checkbox_field=MultiCheckboxField(
                        name='Preserved',
                        visual_region=BoxBounds(x=324, y=1371, width=188, height=66),
                        validator=MultiChoiceValidation.OPTIONAL,
                        checkboxes=[
                            MultiCheckboxOption(name='-20 C', region=BoxBounds(x=333, y=1384, width=12, height=12)),
                            MultiCheckboxOption(name='-80 C', region=BoxBounds(x=333, y=1417, width=12, height=12)),
                            MultiCheckboxOption(name='LN2', region=BoxBounds(x=424, y=1384, width=12, height=12)),
                            MultiCheckboxOption(name='Shield', region=BoxBounds(x=424, y=1417, width=12, height=12)),
                        ],
                    )
                ),
                FormField(
                    text_field=TextField(
                        name='Remarks',
                        visual_region=BoxBounds(x=627, y=1371, width=175, height=66),
                    ),
                ),
            ],
        ),
        FieldGroup(
            name='Liver',
            visual_region=BoxBounds(x=195, y=1442, width=606, height=66),
            fields=[
                FormField(
                    multi_checkbox_field=MultiCheckboxField(
                        name='Preserved',
                        visual_region=BoxBounds(x=324, y=1442, width=188, height=66),
                        validator=MultiChoiceValidation.OPTIONAL,
                        checkboxes=[
                            MultiCheckboxOption(name='-20 C', region=BoxBounds(x=333, y=1455, width=12, height=12)),
                            MultiCheckboxOption(name='-80 C', region=BoxBounds(x=333, y=1488, width=12, height=12)),
                            MultiCheckboxOption(name='LN2', region=BoxBounds(x=424, y=1455, width=12, height=12)),
                            MultiCheckboxOption(name='Shield', region=BoxBounds(x=424, y=1488, width=12, height=12)),
                        ],
                    )
                ),
                FormField(
                    text_field=TextField(
                        name='Remarks',
                        visual_region=BoxBounds(x=627, y=1442, width=175, height=66),
                    ),
                ),
            ],
        ),
        FieldGroup(
            name='Muscle',
            visual_region=BoxBounds(x=195, y=1514, width=606, height=66),
            fields=[
                FormField(
                    multi_checkbox_field=MultiCheckboxField(
                        name='Preserved',
                        visual_region=BoxBounds(x=324, y=1514, width=188, height=66),
                        validator=MultiChoiceValidation.OPTIONAL,
                        checkboxes=[
                            MultiCheckboxOption(name='-20 C', region=BoxBounds(x=333, y=1527, width=12, height=12)),
                            MultiCheckboxOption(name='-80 C', region=BoxBounds(x=333, y=1560, width=12, height=12)),
                            MultiCheckboxOption(name='LN2', region=BoxBounds(x=424, y=1527, width=12, height=12)),
                            MultiCheckboxOption(name='Shield', region=BoxBounds(x=424, y=1560, width=12, height=12)),
                        ],
                    )
                ),
                FormField(
                    text_field=TextField(
                        name='Remarks',
                        visual_region=BoxBounds(x=627, y=1514, width=175, height=66),
                    ),
                ),
            ],
        ),
        FieldGroup(
            name='GI / LI / colon',
            visual_region=BoxBounds(x=195, y=1586, width=606, height=66),
            fields=[
                FormField(
                    circled_field=CircledField(
                        name='Type',
                        visual_region=BoxBounds(x=195, y=1586, width=125, height=69),
                        validator=MultiChoiceValidation.MAXIMUM_ONE,
                        options=[
                            CircledOption(name='GI', region=BoxBounds(x=197, y=1589, width=44, height=32)),
                            CircledOption(name='LI', region=BoxBounds(x=253, y=1588, width=44, height=35)),
                            CircledOption(name='colon', region=BoxBounds(x=203, y=1617, width=92, height=37)),
                        ],
                    )
                ),
                FormField(
                    multi_checkbox_field=MultiCheckboxField(
                        name='Preserved',
                        visual_region=BoxBounds(x=324, y=1586, width=188, height=66),
                        validator=MultiChoiceValidation.OPTIONAL,
                        checkboxes=[
                            MultiCheckboxOption(name='-20 C', region=BoxBounds(x=333, y=1599, width=12, height=12)),
                            MultiCheckboxOption(name='10% form', region=BoxBounds(x=333, y=1632, width=12, height=12)),
                            MultiCheckboxOption(name='LN2', region=BoxBounds(x=424, y=1599, width=12, height=12)),
                            MultiCheckboxOption(name='Shield', region=BoxBounds(x=424, y=1632, width=12, height=12)),
                        ],
                    )
                ),
                FormField(
                    text_field=TextField(
                        name='Remarks',
                        visual_region=BoxBounds(x=627, y=1586, width=175, height=66),
                    ),
                ),
            ],
        ),
        FieldGroup(
            name='Feces',
            visual_region=BoxBounds(x=195, y=1658, width=606, height=66),
            fields=[
                FormField(
                    multi_checkbox_field=MultiCheckboxField(
                        name='Preserved',
                        visual_region=BoxBounds(x=324, y=1658, width=188, height=66),
                        validator=MultiChoiceValidation.OPTIONAL,
                        checkboxes=[
                            MultiCheckboxOption(name='-20 C', region=BoxBounds(x=333, y=1599, width=12, height=12)),
                            MultiCheckboxOption(name='10% form', region=BoxBounds(x=333, y=1632, width=12, height=12)),
                            MultiCheckboxOption(name='LN2', region=BoxBounds(x=424, y=1599, width=12, height=12)),
                            MultiCheckboxOption(name='Shield', region=BoxBounds(x=424, y=1632, width=12, height=12)),
                        ],
                    )
                ),
                FormField(
                    text_field=TextField(
                        name='Remarks',
                        visual_region=BoxBounds(x=627, y=1658, width=175, height=66),
                    ),
                ),
            ],
        ),
        FieldGroup(
            name='Blood',
            visual_region=BoxBounds(x=195, y=1730, width=606, height=66),
            fields=[
                FormField(
                    multi_checkbox_field=MultiCheckboxField(
                        name='Preserved',
                        visual_region=BoxBounds(x=324, y=1730, width=188, height=66),
                        validator=MultiChoiceValidation.OPTIONAL,
                        checkboxes=[
                            MultiCheckboxOption(name='Nobuto', region=BoxBounds(x=333, y=1671, width=12, height=12)),
                            MultiCheckboxOption(name='10% form', region=BoxBounds(x=333, y=1704, width=12, height=12)),
                            MultiCheckboxOption(name='LN2', region=BoxBounds(x=424, y=1671, width=12, height=12)),
                            MultiCheckboxOption(name='Shield', region=BoxBounds(x=424, y=1704, width=12, height=12)),
                        ],
                    )
                ),
                FormField(
                    text_field=TextField(
                        name='Remarks',
                        visual_region=BoxBounds(x=627, y=1730, width=175, height=66),
                    ),
                ),
            ],
        ),
        FieldGroup(
            name='Ecto Parasites 1',
            visual_region=BoxBounds(x=838, y=1301, width=749, height=66),
            fields=[
                FormField(
                    multi_checkbox_field=MultiCheckboxField(
                        name='Type & Count',
                        visual_region=BoxBounds(x=838, y=1301, width=231, height=66),
                        validator=MultiChoiceValidation.OPTIONAL,
                        checkboxes=[
                            MultiCheckboxOption(
                                name='Flea',
                                region=BoxBounds(x=863, y=1310, width=24, height=20),
                                text_region=BoxBounds(x=853, y=1305, width=46, height=26),
                            ),
                            MultiCheckboxOption(
                                name='Tick',
                                region=BoxBounds(x=872, y=1342, width=15, height=17),
                                text_region=BoxBounds(x=854, y=1334, width=46, height=26),
                            ),
                            MultiCheckboxOption(
                                name='Mite',
                                region=BoxBounds(x=973, y=1311, width=16, height=18),
                                text_region=BoxBounds(x=957, y=1305, width=46, height=26),
                            ),
                            MultiCheckboxOption(
                                name='Lice',
                                region=BoxBounds(x=973, y=1341, width=16, height=17),
                                text_region=BoxBounds(x=956, y=1334, width=46, height=26),
                            ),
                        ],
                    )
                ),
                FormField(
                    multi_checkbox_field=MultiCheckboxField(
                        name='Preserved',
                        visual_region=BoxBounds(x=1073, y=1301, width=177, height=66),
                        validator=MultiChoiceValidation.OPTIONAL,
                        checkboxes=[
                            MultiCheckboxOption(name='80%', region=BoxBounds(x=1082, y=1314, width=12, height=12)),
                            MultiCheckboxOption(name='95%', region=BoxBounds(x=1161, y=1314, width=12, height=12)),
                            MultiCheckboxOption(name='LN2', region=BoxBounds(x=1082, y=1347, width=12, height=12)),
                            MultiCheckboxOption(name='Other', region=BoxBounds(x=1159, y=1347, width=12, height=12)),
                        ],
                    )
                ),
                FormField(
                    text_field=TextField(
                        name='Remarks',
                        visual_region=BoxBounds(x=1369, y=1301, width=218, height=66),
                    ),
                ),
            ],
        ),
        FieldGroup(
            name='Ecto Parasites 2',
            visual_region=BoxBounds(x=838, y=1371, width=749, height=66),
            fields=[
                FormField(
                    multi_checkbox_field=MultiCheckboxField(
                        name='Type & Count',
                        visual_region=BoxBounds(x=838, y=1371, width=231, height=66),
                        validator=MultiChoiceValidation.OPTIONAL,
                        checkboxes=[
                            MultiCheckboxOption(
                                name='Flea',
                                region=BoxBounds(x=863, y=1380, width=24, height=20),
                                text_region=BoxBounds(x=853, y=1375, width=46, height=26),
                            ),
                            MultiCheckboxOption(
                                name='Tick',
                                region=BoxBounds(x=872, y=1412, width=15, height=17),
                                text_region=BoxBounds(x=854, y=1404, width=46, height=26),
                            ),
                            MultiCheckboxOption(
                                name='Mite',
                                region=BoxBounds(x=973, y=1381, width=16, height=18),
                                text_region=BoxBounds(x=957, y=1375, width=46, height=26),
                            ),
                            MultiCheckboxOption(
                                name='Lice',
                                region=BoxBounds(x=973, y=1411, width=16, height=17),
                                text_region=BoxBounds(x=956, y=1404, width=46, height=26),
                            ),
                        ],
                    )
                ),
                FormField(
                    multi_checkbox_field=MultiCheckboxField(
                        name='Preserved',
                        visual_region=BoxBounds(x=1073, y=1371, width=177, height=66),
                        validator=MultiChoiceValidation.OPTIONAL,
                        checkboxes=[
                            MultiCheckboxOption(name='80%', region=BoxBounds(x=1082, y=1384, width=12, height=12)),
                            MultiCheckboxOption(name='95%', region=BoxBounds(x=1161, y=1384, width=12, height=12)),
                            MultiCheckboxOption(name='LN2', region=BoxBounds(x=1082, y=1417, width=12, height=12)),
                            MultiCheckboxOption(name='Other', region=BoxBounds(x=1159, y=1417, width=12, height=12)),
                        ],
                    )
                ),
                FormField(
                    text_field=TextField(
                        name='Remarks',
                        visual_region=BoxBounds(x=1369, y=1371, width=218, height=66),
                    ),
                ),
            ],
        ),
        FieldGroup(
            name='Misc Parasites',
            visual_region=BoxBounds(x=835, y=1441, width=754, height=72),
            fields=[
                FormField(
                    text_field=TextField(
                        name='Type',
                        visual_region=BoxBounds(x=838, y=1442, width=231, height=69),
                    ),
                ),
                FormField(
                    text_field=TextField(
                        name='Preserved',
                        visual_region=BoxBounds(x=1073, y=1442, width=177, height=69),
                    ),
                ),
                FormField(
                    text_field=TextField(
                        name='Remarks',
                        visual_region=BoxBounds(x=1369, y=1442, width=218, height=69),
                    ),
                ),
            ],
        ),
        FieldGroup(
            name='Endo Parasites 1',
            visual_region=BoxBounds(x=838, y=1514, width=749, height=69),
            fields=[
                FormField(
                    multi_checkbox_field=MultiCheckboxField(
                        name='Type & Count',
                        visual_region=BoxBounds(x=838, y=1514, width=231, height=69),
                        validator=MultiChoiceValidation.OPTIONAL,
                        checkboxes=[
                            MultiCheckboxOption(
                                name='Nema',
                                region=BoxBounds(x=856, y=1525, width=19, height=18),
                                text_region=BoxBounds(x=842, y=1518, width=45, height=27),
                            ),
                            MultiCheckboxOption(
                                name='Trem',
                                region=BoxBounds(x=858, y=1554, width=20, height=20),
                                text_region=BoxBounds(x=843, y=1550, width=45, height=25),
                            ),
                            MultiCheckboxOption(
                                name='Cest',
                                region=BoxBounds(x=980, y=1527, width=16, height=16),
                                text_region=BoxBounds(x=964, y=1520, width=46, height=25),
                            ),
                            MultiCheckboxOption(
                                name='Cyst',
                                region=BoxBounds(x=982, y=1556, width=16, height=17),
                                text_region=BoxBounds(x=964, y=1551, width=46, height=24),
                            ),
                        ],
                    )
                ),
                FormField(
                    multi_checkbox_field=MultiCheckboxField(
                        name='Preserved',
                        visual_region=BoxBounds(x=1073, y=1514, width=177, height=69),
                        validator=MultiChoiceValidation.OPTIONAL,
                        checkboxes=[
                            MultiCheckboxOption(name='80%', region=BoxBounds(x=1082, y=1527, width=12, height=12)),
                            MultiCheckboxOption(name='LN2', region=BoxBounds(x=1082, y=1560, width=12, height=12)),
                            MultiCheckboxOption(name='Other', region=BoxBounds(x=1168, y=1527, width=12, height=12)),
                        ],
                    )
                ),
                FormField(
                    text_field=TextField(
                        name='Remarks',
                        visual_region=BoxBounds(x=1369, y=1514, width=218, height=69),
                    ),
                ),
            ],
        ),
        FieldGroup(
            name='Endo Parasites 2',
            visual_region=BoxBounds(x=838, y=1586, width=749, height=69),
            fields=[
                FormField(
                    multi_checkbox_field=MultiCheckboxField(
                        name='Type & Count',
                        visual_region=BoxBounds(x=838, y=1586, width=231, height=69),
                        validator=MultiChoiceValidation.OPTIONAL,
                        checkboxes=[
                            MultiCheckboxOption(
                                name='Nema',
                                region=BoxBounds(x=856, y=1598, width=19, height=18),
                                text_region=BoxBounds(x=842, y=1590, width=45, height=27),
                            ),
                            MultiCheckboxOption(
                                name='Trem',
                                region=BoxBounds(x=858, y=1626, width=20, height=20),
                                text_region=BoxBounds(x=843, y=1622, width=45, height=25),
                            ),
                            MultiCheckboxOption(
                                name='Cest',
                                region=BoxBounds(x=980, y=1599, width=16, height=16),
                                text_region=BoxBounds(x=964, y=1592, width=46, height=25),
                            ),
                            MultiCheckboxOption(
                                name='Cyst',
                                region=BoxBounds(x=982, y=1628, width=16, height=17),
                                text_region=BoxBounds(x=964, y=1623, width=46, height=24),
                            ),
                        ],
                    )
                ),
                FormField(
                    multi_checkbox_field=MultiCheckboxField(
                        name='Preserved',
                        visual_region=BoxBounds(x=1073, y=1586, width=177, height=69),
                        validator=MultiChoiceValidation.OPTIONAL,
                        checkboxes=[
                            MultiCheckboxOption(name='80%', region=BoxBounds(x=1082, y=1599, width=12, height=12)),
                            MultiCheckboxOption(name='LN2', region=BoxBounds(x=1082, y=1632, width=12, height=12)),
                            MultiCheckboxOption(name='Other', region=BoxBounds(x=1168, y=1599, width=12, height=12)),
                        ],
                    )
                ),
                FormField(
                    text_field=TextField(
                        name='Remarks',
                        visual_region=BoxBounds(x=1369, y=1586, width=218, height=69),
                    ),
                ),
            ],
        ),
        FieldGroup(
            name='Endo Parasites 3',
            visual_region=BoxBounds(x=838, y=1658, width=749, height=69),
            fields=[
                FormField(
                    multi_checkbox_field=MultiCheckboxField(
                        name='Type & Count',
                        visual_region=BoxBounds(x=838, y=1658, width=231, height=69),
                        validator=MultiChoiceValidation.OPTIONAL,
                        checkboxes=[
                            MultiCheckboxOption(
                                name='Nema',
                                region=BoxBounds(x=856, y=1670, width=19, height=18),
                                text_region=BoxBounds(x=842, y=1662, width=45, height=27),
                            ),
                            MultiCheckboxOption(
                                name='Trem',
                                region=BoxBounds(x=858, y=1698, width=20, height=20),
                                text_region=BoxBounds(x=843, y=1694, width=45, height=25),
                            ),
                            MultiCheckboxOption(
                                name='Cest',
                                region=BoxBounds(x=980, y=1671, width=16, height=16),
                                text_region=BoxBounds(x=964, y=1664, width=46, height=25),
                            ),
                            MultiCheckboxOption(
                                name='Cyst',
                                region=BoxBounds(x=982, y=1700, width=16, height=17),
                                text_region=BoxBounds(x=964, y=1695, width=46, height=24),
                            ),
                        ],
                    )
                ),
                FormField(
                    multi_checkbox_field=MultiCheckboxField(
                        name='Preserved',
                        visual_region=BoxBounds(x=1073, y=1658, width=177, height=69),
                        validator=MultiChoiceValidation.OPTIONAL,
                        checkboxes=[
                            MultiCheckboxOption(name='80%', region=BoxBounds(x=1082, y=1671, width=12, height=12)),
                            MultiCheckboxOption(name='LN2', region=BoxBounds(x=1082, y=1704, width=12, height=12)),
                            MultiCheckboxOption(name='Other', region=BoxBounds(x=1168, y=1671, width=12, height=12)),
                        ],
                    )
                ),
                FormField(
                    text_field=TextField(
                        name='Remarks',
                        visual_region=BoxBounds(x=1369, y=1658, width=218, height=69),
                    ),
                ),
            ],
        ),
        FieldGroup(
            name='Embryos',
            visual_region=BoxBounds(x=838, y=1730, width=749, height=69),
            fields=[
                FormField(
                    text_field=TextField(
                        name='Count',
                        visual_region=BoxBounds(x=872, y=1750, width=45, height=26),
                        text_validator=TextValidator(datatype=TextValidatorDatatype.INTEGER),
                    ),
                ),
                FormField(
                    multi_checkbox_field=MultiCheckboxField(
                        name='Preserved',
                        visual_region=BoxBounds(x=1073, y=1730, width=177, height=69),
                        validator=MultiChoiceValidation.OPTIONAL,
                        checkboxes=[
                            MultiCheckboxOption(name='10% form', region=BoxBounds(x=1082, y=1743, width=12, height=12)),
                            MultiCheckboxOption(name='LN2', region=BoxBounds(x=1082, y=1776, width=12, height=12)),
                            MultiCheckboxOption(name='95%', region=BoxBounds(x=1170, y=1743, width=12, height=12)),
                            MultiCheckboxOption(name='Shield', region=BoxBounds(x=1159, y=1176, width=12, height=12)),
                        ],
                    )
                ),
                FormField(
                    text_field=TextField(
                        name='Remarks',
                        visual_region=BoxBounds(x=1369, y=1730, width=218, height=69),
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
                        name='Tissue Quality',
                        visual_region=BoxBounds(x=372, y=1803, width=462, height=39),
                        validator=MultiChoiceValidation.REQUIRE_ONE,
                        checkboxes=[
                            MultiCheckboxOption(name='Excellent', region=BoxBounds(x=381, y=1822, width=9, height=9)),
                            MultiCheckboxOption(name='Very Good', region=BoxBounds(x=494, y=1822, width=9, height=9)),
                            MultiCheckboxOption(name='Good', region=BoxBounds(x=620, y=1822, width=9, height=9)),
                            MultiCheckboxOption(name='Fair', region=BoxBounds(x=701, y=1822, width=9, height=9)),
                            MultiCheckboxOption(name='Poor', region=BoxBounds(x=767, y=1822, width=9, height=9)),
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
                        name='Time of Death',
                        visual_region=BoxBounds(x=383, y=1838, width=129, height=37),
                        text_validator=TextValidator(
                            datatype=TextValidatorDatatype.TIME,
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
                        name='Time of Tissue in LN2',
                        visual_region=BoxBounds(x=773, y=1838, width=114, height=37),
                        text_validator=TextValidator(
                            datatype=TextValidatorDatatype.TIME,
                        ),
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
                        name='Elapsed Time (min)',
                        visual_region=BoxBounds(x=383, y=1882, width=128, height=36),
                        text_validator=TextValidator(
                            datatype=TextValidatorDatatype.INTEGER,
                        ),
                    )
                ),
            ],
        ),
        FieldGroup(
            name='Cold Chain Progression',
            visual_region=BoxBounds(x=903, y=1834, width=681, height=90),
            fields=[
                FormField(
                    text_field=TextField(
                        name='Dry Ice',
                        visual_region=BoxBounds(x=920, y=1840, width=148, height=38),
                        text_validator=TextValidator(
                            datatype=TextValidatorDatatype.DATE,
                        ),
                    )
                ),
                FormField(
                    text_field=TextField(
                        name='Field LN2',
                        visual_region=BoxBounds(x=1156, y=1836, width=143, height=42),
                        text_validator=TextValidator(
                            datatype=TextValidatorDatatype.DATE,
                        ),
                    )
                ),
                FormField(
                    text_field=TextField(
                        name='-20 C',
                        visual_region=BoxBounds(x=1374, y=1835, width=147, height=43),
                        text_validator=TextValidator(
                            datatype=TextValidatorDatatype.DATE,
                        ),
                    )
                ),
                FormField(
                    text_field=TextField(
                        name='-40 C',
                        visual_region=BoxBounds(x=923, y=1881, width=142, height=41),
                        text_validator=TextValidator(
                            datatype=TextValidatorDatatype.DATE,
                        ),
                    )
                ),
                FormField(
                    text_field=TextField(
                        name='-80 C',
                        visual_region=BoxBounds(x=1159, y=1882, width=141, height=40),
                        text_validator=TextValidator(
                            datatype=TextValidatorDatatype.DATE,
                        ),
                    )
                ),
                FormField(
                    text_field=TextField(
                        name='Install LN2',
                        visual_region=BoxBounds(x=1377, y=1881, width=144, height=41),
                        text_validator=TextValidator(
                            datatype=TextValidatorDatatype.DATE,
                        ),
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
