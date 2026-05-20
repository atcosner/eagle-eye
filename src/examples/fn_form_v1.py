import logging
import shutil
from pathlib import Path
from sqlalchemy.orm import Session

from src.database.exporters.circled_exporter import CircledExporter
from src.database.exporters.multi_checkbox_exporter import MultiCheckboxExporter
from src.database.exporters.text_exporter import TextExporter
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
from src.util.export import MultiCbExportType, CapitalizationType, ExportType
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
            name='Control Data',
            visual_region=None,
            fields=[
                FormField(
                    text_field=TextField(
                        name='Data entered by:',
                        visual_region=BoxBounds(x=0, y=0, width=0, height=0),
                        synthetic_only=True,
                        exporters=[
                            TextExporter(export_field_name='entered_by'),
                        ],
                    ),
                ),
                FormField(
                    text_field=TextField(
                        name='Entered on:',
                        visual_region=BoxBounds(x=0, y=0, width=0, height=0),
                        synthetic_only=True,
                        text_validator=TextValidator(datatype=TextValidatorDatatype.DATE),
                        exporters=[
                            TextExporter(export_field_name='entered_on'),
                        ],
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
                        visual_region=BoxBounds(x=500, y=69, width=330, height=84),
                        text_validator=TextValidator(
                            text_regex=r'^[0-9]{4}-PA[0-9]{1,3}$',
                            error_tooltip='Pseudo-Accession must be in the format: <YYYY>-PA<NUMBER>',
                        ),
                        exporters=[
                            TextExporter(export_field_name='pseudo-accn', capitalization=CapitalizationType.UPPER),
                        ],
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
                        visual_region=BoxBounds(x=1552, y=90, width=363, height=63),
                        text_validator=TextValidator(
                            datatype=TextValidatorDatatype.INTEGER,
                            text_required=False,
                        ),
                        exporters=[
                            TextExporter(export_field_name='catalog#'),
                        ],
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
                        visual_region=BoxBounds(x=2086, y=86, width=272, height=92),
                        text_validator=TextValidator(
                            text_regex=r'^FN[0-9]{6}$',
                            error_tooltip='FN Numbers must be exactly 6 digits',
                        ),
                        exporters=[
                            TextExporter(export_field_name='FN#', capitalization=CapitalizationType.UPPER),
                        ],
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
                        visual_region=BoxBounds(x=478, y=254, width=766, height=68),
                        text_validator=TextValidator(
                            datatype=TextValidatorDatatype.LIST_CHOICE,
                            allow_closest_match_correction=True,
                            text_choices=[TextChoice(text=t) for t in species_list],
                        ),
                        exporters=[
                            TextExporter(capitalization=CapitalizationType.TITLE),
                        ],
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
                        visual_region=BoxBounds(x=1362, y=252, width=315, height=69),
                        text_validator=TextValidator(
                            datatype=TextValidatorDatatype.LIST_CHOICE,
                            allow_closest_match_correction=True,
                            text_choices=[TextChoice(text=t) for t in agent_list],
                        ),
                        exporters=[
                            TextExporter(export_field_name='ID_by', capitalization=CapitalizationType.UPPER),
                        ],
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
                        visual_region=BoxBounds(x=1683, y=264, width=686, height=70),
                        validator=MultiChoiceValidation.REQUIRE_ONE,
                        checkboxes=[
                            MultiCheckboxOption(name='Low', region=BoxBounds(x=1986, y=290, width=18, height=21)),
                            MultiCheckboxOption(name='Medium', region=BoxBounds(x=2108, y=290, width=18, height=21)),
                            MultiCheckboxOption(name='High', region=BoxBounds(x=2248, y=290, width=18, height=21)),
                        ],
                        exporter=MultiCheckboxExporter(
                            export_field_name='ID_confidence',
                            export_type=MultiCbExportType.SINGLE_COLUMN,
                            capitalization=CapitalizationType.LOWER,
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
                        visual_region=BoxBounds(x=657, y=330, width=374, height=68),
                        text_validator=TextValidator(
                            text_regex=r'^[A-Z]{3,4}[0-9]{1,3}$',
                            error_tooltip='GPS Waypoint ID must be 3-4 letters followed by 1-3 numbers',
                        ),
                        exporters=[
                            TextExporter(export_field_name='GPS_waypoint_ID', capitalization=CapitalizationType.UPPER),
                        ],
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
                        visual_region=BoxBounds(x=1257, y=336, width=370, height=62),
                        exporters=[
                            TextExporter(export_field_name='trapline_ID', capitalization=CapitalizationType.UPPER),
                        ],
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
                        visual_region=BoxBounds(x=1968, y=336, width=394, height=62),
                        exporters=[
                            TextExporter(export_field_name='BlueCard_other#', capitalization=CapitalizationType.UPPER),
                        ],
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
                        visual_region=BoxBounds(x=664, y=417, width=1047, height=68),
                        text_validator=TextValidator(
                            datatype=TextValidatorDatatype.CSV_OF_CHOICE,
                            allow_closest_match_correction=True,
                            text_choices=[TextChoice(text=t) for t in agent_list],
                        ),
                        exporters=[
                            TextExporter(export_field_name='collector', capitalization=CapitalizationType.UPPER),
                        ],
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
                        visual_region=BoxBounds(x=1904, y=423, width=471, height=62),
                        text_validator=TextValidator(
                            datatype=TextValidatorDatatype.DATE,
                        ),
                        exporters=[
                            TextExporter(export_field_name='coll_date(verbatim)', capitalization=CapitalizationType.TITLE),
                            TextExporter(export_field_name='coll_date(DO-MO-YEAR)', export_type=ExportType.DATE_DMY),
                        ],
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
                        visual_region=BoxBounds(x=660, y=506, width=339, height=69),
                        text_validator=TextValidator(
                            datatype=TextValidatorDatatype.CSV_OF_CHOICE,
                            allow_closest_match_correction=True,
                            text_choices=[TextChoice(text=t) for t in agent_list],
                        ),
                        exporters=[
                            TextExporter(export_field_name='preparator', capitalization=CapitalizationType.UPPER),
                        ],
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
                        visual_region=BoxBounds(x=1203, y=506, width=339, height=69),
                        text_validator=TextValidator(
                            datatype=TextValidatorDatatype.DATE,
                        ),
                        exporters=[
                            TextExporter(export_field_name='prep_date(verbatim)', capitalization=CapitalizationType.TITLE),
                            TextExporter(export_field_name='prep_date(DO-MO-YEAR)', export_type=ExportType.DATE_DMY),
                        ],
                    ),
                ),
            ],
        ),
        FieldGroup(
            name='Tissue By',
            visual_region=BoxBounds(x=1857, y=513, width=510, height=62),
            fields=[
                FormField(
                    text_field=TextField(
                        name='Initials',
                        visual_region=BoxBounds(x=1846, y=496, width=159, height=78),
                        text_validator=TextValidator(
                            datatype=TextValidatorDatatype.LIST_CHOICE,
                            allow_closest_match_correction=True,
                            text_choices=[TextChoice(text=t) for t in agent_list],
                        ),
                        exporters=[
                            TextExporter(export_field_name='tissueby', capitalization=CapitalizationType.UPPER),
                        ],
                    ),
                ),
                FormField(
                    text_field=TextField(
                        name='Date',
                        visual_region=BoxBounds(x=2012, y=512, width=351, height=64),
                        text_validator=TextValidator(
                            datatype=TextValidatorDatatype.DATE,
                        ),
                        exporters=[
                            TextExporter(export_field_name='tissueby_date(verbatim)', capitalization=CapitalizationType.TITLE),
                            TextExporter(export_field_name='tissueby_date(DO-MO-YEAR)', export_type=ExportType.DATE_DMY),
                        ],
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
                        visual_region=BoxBounds(x=588, y=633, width=930, height=68),
                        text_validator=TextValidator(
                            datatype=TextValidatorDatatype.FN_COUNTRY_STATE,
                            text_regex=r"([a-zA-Z ]*)\/([a-zA-Z ]*)",
                            custom_data={
                                0: CustomData(key=0, text_choices=[TextChoice(text=t) for t in country_list]),
                                1: CustomData(key=1, text_choices=[TextChoice(text=t) for t in state_list]),
                            },
                        ),
                        exporters=[
                            TextExporter(
                                export_field_name='country',
                                export_type=ExportType.VALIDATOR_PART,
                                strip_value=True,
                                validator_group_index=0,
                            ),
                            TextExporter(
                                export_field_name='state_province',
                                export_type=ExportType.VALIDATOR_PART,
                                strip_value=True,
                                validator_group_index=1,
                            ),
                        ],
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
                        visual_region=BoxBounds(x=1670, y=636, width=692, height=64),
                        text_validator=TextValidator(
                            datatype=TextValidatorDatatype.LIST_CHOICE,
                            allow_closest_match_correction=True,
                            text_choices=[TextChoice(text=t) for t in county_list],
                        ),
                        exporters=[
                            TextExporter(capitalization=CapitalizationType.TITLE),
                        ],
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
                        visual_region=BoxBounds(x=474, y=708, width=1896, height=64),
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
                        visual_region=BoxBounds(x=392, y=782, width=646, height=63),
                        text_validator=TextValidator(
                            datatype=TextValidatorDatatype.GPS_POINT_DD,
                            text_required=False,
                        ),
                        exporters=[
                            TextExporter(export_field_name='latitude_dec'),
                        ],
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
                        visual_region=BoxBounds(x=1158, y=782, width=651, height=63),
                        text_validator=TextValidator(
                            datatype=TextValidatorDatatype.GPS_POINT_DD,
                            text_required=False,
                        ),
                        exporters=[
                            TextExporter(export_field_name='longitude_dec'),
                        ],
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
                        visual_region=BoxBounds(x=2050, y=782, width=320, height=63),
                        text_validator=TextValidator(
                            datatype=TextValidatorDatatype.INTEGER,
                            text_required=False,
                        ),
                        exporters=[
                            TextExporter(export_field_name='altitude(m)'),
                        ],
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
                        visual_region=BoxBounds(x=502, y=855, width=502, height=68),
                        text_validator=TextValidator(
                            datatype=TextValidatorDatatype.INTEGER,
                            text_required=False,
                        ),
                        exporters=[
                            TextExporter(export_field_name='error(m)'),
                        ],
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
                        visual_region=BoxBounds(x=1164, y=858, width=460, height=69),
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
                        visual_region=BoxBounds(x=2014, y=862, width=348, height=62),
                        text_validator=TextValidator(
                            text_regex=r'^FN[0-9]{6}$',
                            error_tooltip='FN Numbers must be exactly 6 digits',
                            text_required=False,
                        ),
                        exporters=[
                            TextExporter(export_field_name='locality_same_as', capitalization=CapitalizationType.UPPER),
                        ],
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
            visual_region=BoxBounds(x=608, y=957, width=1634, height=118),
            fields=[
                FormField(
                    text_field=TextField(
                        name='Total (mm)',
                        visual_region=BoxBounds(x=612, y=958, width=156, height=68),
                        text_validator=TextValidator(
                            datatype=TextValidatorDatatype.INTEGER,
                        ),
                        exporters=[
                            TextExporter(export_field_name='total(mm)'),
                        ],
                    ),
                ),
                FormField(
                    text_field=TextField(
                        name='Tail (mm)',
                        visual_region=BoxBounds(x=774, y=957, width=154, height=69),
                        text_validator=TextValidator(
                            datatype=TextValidatorDatatype.INTEGER,
                        ),
                        exporters=[
                            TextExporter(export_field_name='tail(mm)'),
                        ],
                    ),
                ),
                FormField(
                    text_field=TextField(
                        name='Hindfoot (mm)',
                        visual_region=BoxBounds(x=933, y=956, width=150, height=70),
                        text_validator=TextValidator(
                            datatype=TextValidatorDatatype.INTEGER,
                        ),
                        exporters=[
                            TextExporter(export_field_name='hindfoot(mm)'),
                        ],
                    ),
                ),
                FormField(
                    text_field=TextField(
                        name='Ear (mm)',
                        visual_region=BoxBounds(x=1084, y=956, width=156, height=70),
                        text_validator=TextValidator(
                            datatype=TextValidatorDatatype.INTEGER,
                        ),
                        exporters=[
                            TextExporter(export_field_name='ear(mm)'),
                        ],
                    ),
                ),
                FormField(
                    text_field=TextField(
                        name='Weight (g)',
                        visual_region=BoxBounds(x=1245, y=956, width=156, height=70),
                        text_validator=TextValidator(
                            datatype=TextValidatorDatatype.INTEGER,
                        ),
                        exporters=[
                            TextExporter(export_field_name='weight(g)'),
                        ],
                    ),
                ),
                FormField(
                    text_field=TextField(
                        name='Measured by',
                        visual_region=BoxBounds(x=1432, y=956, width=339, height=70),
                        text_validator=TextValidator(
                            datatype=TextValidatorDatatype.LIST_CHOICE,
                            allow_closest_match_correction=True,
                            text_choices=[TextChoice(text=t) for t in agent_list],
                        ),
                        exporters=[
                            TextExporter(capitalization=CapitalizationType.UPPER),
                        ],
                    ),
                ),
                FormField(
                    text_field=TextField(
                        name='Bats: forearm (mm)',
                        visual_region=BoxBounds(x=1896, y=957, width=162, height=69),
                        text_validator=TextValidator(
                            datatype=TextValidatorDatatype.INTEGER,
                            text_required=False,
                        ),
                        exporters=[
                            TextExporter(export_field_name='forearm(mm)'),
                        ],
                    ),
                ),
                FormField(
                    text_field=TextField(
                        name='Bats: tragus (mm)',
                        visual_region=BoxBounds(x=2062, y=957, width=165, height=69),
                        text_validator=TextValidator(
                            datatype=TextValidatorDatatype.INTEGER,
                            text_required=False,
                        ),
                        exporters=[
                            TextExporter(export_field_name='tragus(mm)'),
                        ],
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
                        visual_region=BoxBounds(x=310, y=1095, width=860, height=66),
                        validator=MultiChoiceValidation.REQUIRE_ONE,
                        checkboxes=[
                            MultiCheckboxOption(name='Adult', region=BoxBounds(x=519, y=1119, width=16, height=18)),
                            MultiCheckboxOption(name='Subadult', region=BoxBounds(x=670, y=1119, width=16, height=18)),
                            MultiCheckboxOption(name='Juvenile', region=BoxBounds(x=801, y=1119, width=16, height=18)),
                            MultiCheckboxOption(name='Embryo', region=BoxBounds(x=924, y=1119, width=16, height=18)),
                            MultiCheckboxOption(name='Unknown', region=BoxBounds(x=1066, y=1119, width=16, height=18)),
                        ],
                        exporter=MultiCheckboxExporter(
                            export_type=MultiCbExportType.SINGLE_COLUMN,
                            capitalization=CapitalizationType.LOWER,
                        ),
                    )
                ),
            ],
        ),
        FieldGroup(
            name='Relationship',
            visual_region=BoxBounds(x=1344, y=1088, width=1028, height=81),
            fields=[
                FormField(
                    text_field=TextField(
                        name='Type',
                        visual_region=BoxBounds(x=1593, y=1096, width=384, height=51),
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
                        exporters=[
                            TextExporter(export_field_name='relate_type'),
                        ],
                    ),
                ),
                FormField(
                    text_field=TextField(
                        name='Other ID',
                        visual_region=BoxBounds(x=2048, y=1092, width=309, height=56),
                        text_validator=TextValidator(
                            text_regex=r'^FN[0-9]{6}$',
                            error_tooltip='FN Numbers must be exactly 6 digits',
                        ),
                        exporters=[
                            TextExporter(export_field_name='relate_otherID'),
                        ],
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
                        name='Sex',
                        visual_region=BoxBounds(x=300, y=1173, width=700, height=309),
                        validator=MultiChoiceValidation.REQUIRE_ONE,
                        checkboxes=[
                            MultiCheckboxOption(name='Male', region=BoxBounds(x=324, y=1209, width=16, height=18)),
                            MultiCheckboxOption(name='Female', region=BoxBounds(x=324, y=1292, width=16, height=18)),
                            MultiCheckboxOption(name='Sex Unknown', region=BoxBounds(x=324, y=1437, width=16, height=18)),
                            MultiCheckboxOption(name='Sex Not Examined', region=BoxBounds(x=644, y=1437, width=16, height=18)),
                        ],
                        exporter=MultiCheckboxExporter(
                            export_type=MultiCbExportType.SINGLE_COLUMN,
                            capitalization=CapitalizationType.LOWER,
                        ),
                    )
                ),
            ],
        ),
        FieldGroup(
            name='Male',
            visual_region=BoxBounds(x=300, y=1188, width=1390, height=72),
            fields=[
                FormField(
                    multi_checkbox_field=MultiCheckboxField(
                        name='External',
                        visual_region=BoxBounds(x=530, y=1190, width=632, height=54),
                        validator=MultiChoiceValidation.REQUIRE_ONE,
                        checkboxes=[
                            MultiCheckboxOption(name='Scrotal', region=BoxBounds(x=724, y=1209, width=16, height=18)),
                            MultiCheckboxOption(name='Non-scrotal', region=BoxBounds(x=926, y=1209, width=16, height=18)),
                        ],
                        exporter=MultiCheckboxExporter(
                            export_field_name='male_external',
                            export_type=MultiCbExportType.SINGLE_COLUMN,
                            capitalization=CapitalizationType.LOWER,
                        ),
                    )
                ),
                FormField(
                    text_field=TextField(
                        name='Testes',
                        visual_region=BoxBounds(x=1362, y=1180, width=234, height=56),
                        text_validator=TextValidator(
                            text_regex=r'^[0-9]+[x][0-9]+$',
                            error_tooltip='Measurement must be: [Length]x[Width]',
                        ),
                        exporters=[
                            TextExporter(export_field_name='T=LxW(mm)'),
                        ],
                    ),
                ),
            ],
        ),
        FieldGroup(
            name='Female',
            visual_region=BoxBounds(x=298, y=1262, width=2076, height=147),
            fields=[
                FormField(
                    multi_checkbox_field=MultiCheckboxField(
                        name='Vagina',
                        visual_region=BoxBounds(x=525, y=1269, width=522, height=63),
                        validator=MultiChoiceValidation.NONE,
                        checkboxes=[
                            MultiCheckboxOption(name='Open', region=BoxBounds(x=699, y=1292, width=16, height=18)),
                            MultiCheckboxOption(name='Closed', region=BoxBounds(x=876, y=1292, width=16, height=18)),
                        ],
                        exporter=MultiCheckboxExporter(
                            export_type=MultiCbExportType.SINGLE_COLUMN,
                            capitalization=CapitalizationType.LOWER,
                        ),
                    )
                ),
                FormField(
                    multi_checkbox_field=MultiCheckboxField(
                        name='Mammae',
                        visual_region=BoxBounds(x=1080, y=1270, width=573, height=60),
                        validator=MultiChoiceValidation.NONE,
                        checkboxes=[
                            MultiCheckboxOption(name='Enlarged', region=BoxBounds(x=1287, y=1292, width=16, height=18)),
                            MultiCheckboxOption(name='Small', region=BoxBounds(x=1521, y=1292, width=16, height=18)),
                        ],
                        exporter=MultiCheckboxExporter(
                            export_type=MultiCbExportType.SINGLE_COLUMN,
                            capitalization=CapitalizationType.LOWER,
                        ),
                    )
                ),
                FormField(
                    multi_checkbox_field=MultiCheckboxField(
                        name='Lactation',
                        visual_region=BoxBounds(x=1708, y=1278, width=664, height=50),
                        validator=MultiChoiceValidation.NONE,
                        checkboxes=[
                            MultiCheckboxOption(name='Lactating', region=BoxBounds(x=1905, y=1292, width=16, height=18)),
                            MultiCheckboxOption(name='Not Lactating', region=BoxBounds(x=2132, y=1292, width=16, height=18)),
                        ],
                        exporter=MultiCheckboxExporter(
                            export_type=MultiCbExportType.SINGLE_COLUMN,
                            capitalization=CapitalizationType.LOWER,
                        ),
                    )
                ),
                FormField(
                    circled_field=CircledField(
                        name='Placental Scars',
                        visual_region=BoxBounds(x=909, y=1324, width=166, height=86),
                        validator=MultiChoiceValidation.MAXIMUM_ONE,
                        options=[
                            CircledOption(name='Yes', region=BoxBounds(x=915, y=1330, width=70, height=68)),
                            CircledOption(name='No', region=BoxBounds(x=1002, y=1332, width=64, height=69)),
                        ],
                        exporter=CircledExporter(export_field_name='plsc(y/n)'),
                    )
                ),
                FormField(
                    text_field=TextField(
                        name='Placental Scars - Measurements',
                        visual_region=BoxBounds(x=1066, y=1326, width=284, height=90),
                        text_regions=[
                            BoxBounds(x=1089, y=1344, width=123, height=52),
                            BoxBounds(x=1216, y=1346, width=110, height=48),
                        ],
                        text_validator=TextValidator(
                            text_regex=r'^[0-9]+R,[0-9]+L$',
                            error_tooltip='Measurement must be: [integer]R,[integer]L',
                        ),
                        exporters=[
                            TextExporter(export_field_name='plsc_R-L', prefix='plsc='),
                        ],
                    )
                ),
                FormField(
                    circled_field=CircledField(
                        name='Embryo',
                        visual_region=BoxBounds(x=1560, y=1323, width=164, height=87),
                        validator=MultiChoiceValidation.MAXIMUM_ONE,
                        options=[
                            CircledOption(name='Yes', region=BoxBounds(x=1568, y=1335, width=69, height=66)),
                            CircledOption(name='No', region=BoxBounds(x=1648, y=1334, width=69, height=68)),
                        ],
                        exporter=CircledExporter(export_field_name='emb(y/n)'),
                    )
                ),
                FormField(
                    text_field=TextField(
                        name='Embryo - Measurements',
                        visual_region=BoxBounds(x=1714, y=1336, width=276, height=69),
                        text_regions=[
                            BoxBounds(x=1737, y=1346, width=240, height=52),
                        ],
                        text_validator=TextValidator(
                            text_regex=r'^[0-9]+R,[0-9]+L$',
                            error_tooltip='Measurement must be: [integer]R,[integer]L',
                        ),
                        exporters=[
                            TextExporter(export_field_name='emb_R-L', prefix='emb='),
                        ],
                    )
                ),
                FormField(
                    text_field=TextField(
                        name='Embryo - CR',
                        visual_region=BoxBounds(x=2084, y=1329, width=128, height=57),
                        text_validator=TextValidator(
                            datatype=TextValidatorDatatype.INTEGER,
                            text_required=False,
                        ),
                        exporters=[
                            TextExporter(export_field_name='emb_CR(mm)', prefix='CR='),
                        ],
                    )
                ),
            ],
        ),
        FieldGroup(
            name='Ecto Parasites',
            visual_region=BoxBounds(x=298, y=1484, width=2064, height=75),
            fields=[
                FormField(
                    circled_field=CircledField(
                        name='Exam?',
                        visual_region=BoxBounds(x=306, y=1488, width=372, height=62),
                        validator=MultiChoiceValidation.MAXIMUM_ONE,
                        options=[
                            CircledOption(name='Yes', region=BoxBounds(x=531, y=1491, width=58, height=57)),
                            CircledOption(name='No', region=BoxBounds(x=606, y=1488, width=62, height=60)),
                        ],
                        exporter=CircledExporter(export_field_name='ecto_exam(y/n)'),
                    )
                ),
                FormField(
                    circled_field=CircledField(
                        name='Found?',
                        visual_region=BoxBounds(x=669, y=1486, width=393, height=62),
                        validator=MultiChoiceValidation.MAXIMUM_ONE,
                        options=[
                            CircledOption(name='Yes', region=BoxBounds(x=904, y=1488, width=62, height=60)),
                            CircledOption(name='No', region=BoxBounds(x=987, y=1485, width=60, height=63)),
                        ],
                        exporter=CircledExporter(export_field_name='ecto_found(y/n)'),
                    )
                ),
                FormField(
                    text_field=TextField(
                        name='By',
                        visual_region=BoxBounds(x=1130, y=1488, width=225, height=50),
                        text_validator=TextValidator(
                            datatype=TextValidatorDatatype.LIST_CHOICE,
                            allow_closest_match_correction=True,
                            text_choices=[TextChoice(text=t) for t in agent_list],
                        ),
                        exporters=[
                            TextExporter(export_field_name='ecto_by', capitalization=CapitalizationType.UPPER),
                        ],
                    ),
                ),
                FormField(
                    text_field=TextField(
                        name='Date',
                        visual_region=BoxBounds(x=1448, y=1485, width=224, height=52),
                        text_validator=TextValidator(
                            datatype=TextValidatorDatatype.DATE,
                        ),
                        exporters=[
                            TextExporter(export_field_name='ecto_coll(verbatim)'),
                            TextExporter(export_field_name='ecto_coll(DO-MO-YEAR)', export_type=ExportType.DATE_DMY),
                        ],
                    ),
                ),
                FormField(
                    text_field=TextField(
                        name='Method',
                        visual_region=BoxBounds(x=1812, y=1479, width=552, height=58),
                        exporters=[
                            TextExporter(export_field_name='ecto_method'),
                        ],
                    ),
                ),
            ],
        ),
        FieldGroup(
            name='Endo Parasites',
            visual_region=BoxBounds(x=306, y=1556, width=2060, height=70),
            fields=[
                FormField(
                    circled_field=CircledField(
                        name='Exam?',
                        visual_region=BoxBounds(x=309, y=1563, width=370, height=60),
                        validator=MultiChoiceValidation.MAXIMUM_ONE,
                        options=[
                            CircledOption(name='Yes', region=BoxBounds(x=537, y=1564, width=66, height=58)),
                            CircledOption(name='No', region=BoxBounds(x=620, y=1560, width=60, height=66)),
                        ],
                        exporter=CircledExporter(export_field_name='endo_exam(y/n)'),
                    )
                ),
                FormField(
                    circled_field=CircledField(
                        name='Found?',
                        visual_region=BoxBounds(x=680, y=1558, width=372, height=68),
                        validator=MultiChoiceValidation.MAXIMUM_ONE,
                        options=[
                            CircledOption(name='Yes', region=BoxBounds(x=912, y=1562, width=58, height=63)),
                            CircledOption(name='No', region=BoxBounds(x=988, y=1566, width=64, height=60)),
                        ],
                        exporter=CircledExporter(export_field_name='endo_found(y/n)'),
                    )
                ),
                FormField(
                    text_field=TextField(
                        name='By',
                        visual_region=BoxBounds(x=1130, y=1556, width=231, height=57),
                        text_validator=TextValidator(
                            datatype=TextValidatorDatatype.LIST_CHOICE,
                            allow_closest_match_correction=True,
                            text_choices=[TextChoice(text=t) for t in agent_list],
                        ),
                        exporters=[
                            TextExporter(export_field_name='endo_by', capitalization=CapitalizationType.UPPER),
                        ],
                    ),
                ),
                FormField(
                    text_field=TextField(
                        name='Date',
                        visual_region=BoxBounds(x=1450, y=1558, width=224, height=54),
                        text_validator=TextValidator(
                            datatype=TextValidatorDatatype.DATE,
                            text_required=False,
                        ),
                        exporters=[
                            TextExporter(export_field_name='endo_coll(verbatim)', capitalization=CapitalizationType.TITLE),
                            TextExporter(export_field_name='endo_coll(DO-MO-YEAR)', export_type=ExportType.DATE_DMY),
                        ],
                    ),
                ),
                FormField(
                    text_field=TextField(
                        name='Method',
                        visual_region=BoxBounds(x=1815, y=1558, width=543, height=54),
                        exporters=[
                            TextExporter(export_field_name='endo_method'),
                        ],
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
                        visual_region=BoxBounds(x=573, y=1652, width=1800, height=92),
                        validator=MultiChoiceValidation.REQUIRE_ONE,
                        checkboxes=[
                            MultiCheckboxOption(name='Skin', region=BoxBounds(x=615, y=1692, width=18, height=18)),
                            MultiCheckboxOption(name='Skull', region=BoxBounds(x=764, y=1692, width=18, height=18)),
                            MultiCheckboxOption(name='Skull + Skel', region=BoxBounds(x=932, y=1692, width=18, height=18)),
                            MultiCheckboxOption(
                                name='Whole Org',
                                region=BoxBounds(x=1206, y=1692, width=18, height=18),
                                circled_options=[
                                    SubCircledOption(name='95% EtOH', region=BoxBounds(x=1434, y=1650, width=106, height=87)),
                                    SubCircledOption(name='Frozen', region=BoxBounds(x=1558, y=1659, width=81, height=86)),
                                ]
                            ),
                            MultiCheckboxOption(name='Tissue only', region=BoxBounds(x=1688, y=1692, width=18, height=18)),
                            MultiCheckboxOption(
                                name='Other',
                                region=BoxBounds(x=1980, y=1692, width=18, height=18),
                                text_region=BoxBounds(x=2122, y=1654, width=237, height=64),
                            ),
                        ],
                        exporter=MultiCheckboxExporter(
                            export_field_name='prep_type(s)',
                            export_type=MultiCbExportType.SINGLE_PLUS_TEXT,
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
                    multi_checkbox_field=MultiCheckboxField(
                        name='Collection Method',
                        visual_region=BoxBounds(x=405, y=1744, width=1725, height=78),
                        validator=MultiChoiceValidation.REQUIRE_ONE,
                        checkboxes=[
                            MultiCheckboxOption(name='Sherman', region=BoxBounds(x=428, y=1774, width=18, height=18)),
                            MultiCheckboxOption(name='Snap', region=BoxBounds(x=614, y=1774, width=18, height=18)),
                            MultiCheckboxOption(name='Rat', region=BoxBounds(x=765, y=1774, width=18, height=18)),
                            MultiCheckboxOption(name='Gopher', region=BoxBounds(x=888, y=1774, width=18, height=18)),
                            MultiCheckboxOption(name='Pit', region=BoxBounds(x=1036, y=1774, width=18, height=18)),
                            MultiCheckboxOption(name='Net', region=BoxBounds(x=1144, y=1774, width=18, height=18)),
                            MultiCheckboxOption(name='Gun', region=BoxBounds(x=1268, y=1774, width=18, height=18)),
                            MultiCheckboxOption(name='Salvage', region=BoxBounds(x=1402, y=1774, width=18, height=18)),
                            MultiCheckboxOption(name='Tomahawk', region=BoxBounds(x=1602, y=1774, width=18, height=18)),
                            MultiCheckboxOption(
                                name='Other',
                                region=BoxBounds(x=1773, y=1774, width=18, height=18),
                                text_region=BoxBounds(x=1898, y=1738, width=216, height=63),
                            ),
                        ],
                        exporter=MultiCheckboxExporter(
                            export_field_name='trap_type',
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
                    circled_field=CircledField(
                        name='DOA',
                        visual_region=BoxBounds(x=2122, y=1742, width=255, height=81),
                        validator=MultiChoiceValidation.REQUIRE_ONE,
                        options=[
                            CircledOption(name='Yes', region=BoxBounds(x=2244, y=1760, width=50, height=50)),
                            CircledOption(name='No', region=BoxBounds(x=2310, y=1758, width=50, height=50)),
                        ],
                        exporter=CircledExporter(export_field_name='dead_on_arrival(y/n)'),
                    )
                ),
            ],
        ),
        FieldGroup(
            name='Heart, Lung',
            visual_region=BoxBounds(x=292, y=1952, width=909, height=99),
            fields=[
                FormField(
                    multi_checkbox_field=MultiCheckboxField(
                        name='Preserved',
                        visual_region=BoxBounds(x=486, y=1952, width=282, height=99),
                        validator=MultiChoiceValidation.OPTIONAL,
                        checkboxes=[
                            MultiCheckboxOption(name='-20 C', region=BoxBounds(x=500, y=1971, width=18, height=18)),
                            MultiCheckboxOption(name='-80 C', region=BoxBounds(x=500, y=2020, width=18, height=18)),
                            MultiCheckboxOption(name='LN2', region=BoxBounds(x=636, y=1971, width=18, height=18)),
                            MultiCheckboxOption(name='Shield', region=BoxBounds(x=636, y=2020, width=18, height=18)),
                        ],
                        exporter=MultiCheckboxExporter(
                            export_field_name='Heart,Lung_pres',
                            export_type=MultiCbExportType.SINGLE_COLUMN,
                        ),
                    )
                ),
                FormField(
                    text_field=TextField(
                        name='Remarks',
                        visual_region=BoxBounds(x=940, y=1952, width=262, height=99),
                        exporters=[
                            TextExporter(export_field_name='H/L_remarks'),
                        ],
                    ),
                ),
            ],
        ),
        FieldGroup(
            name='Kidney, Spleen',
            visual_region=BoxBounds(x=292, y=2056, width=909, height=99),
            fields=[
                FormField(
                    multi_checkbox_field=MultiCheckboxField(
                        name='Preserved',
                        visual_region=BoxBounds(x=486, y=2056, width=282, height=99),
                        validator=MultiChoiceValidation.OPTIONAL,
                        checkboxes=[
                            MultiCheckboxOption(name='-20 C', region=BoxBounds(x=500, y=2076, width=18, height=18)),
                            MultiCheckboxOption(name='-80 C', region=BoxBounds(x=500, y=2126, width=18, height=18)),
                            MultiCheckboxOption(name='LN2', region=BoxBounds(x=636, y=2076, width=18, height=18)),
                            MultiCheckboxOption(name='Shield', region=BoxBounds(x=636, y=2126, width=18, height=18)),
                        ],
                        exporter=MultiCheckboxExporter(
                            export_field_name='Kidney,Spleen_pres',
                            export_type=MultiCbExportType.SINGLE_COLUMN,
                        ),
                    )
                ),
                FormField(
                    text_field=TextField(
                        name='Remarks',
                        visual_region=BoxBounds(x=940, y=2056, width=262, height=99),
                        exporters=[
                            TextExporter(export_field_name='K/Sp_remarks'),
                        ],
                    ),
                ),
            ],
        ),
        FieldGroup(
            name='Liver',
            visual_region=BoxBounds(x=292, y=2163, width=909, height=99),
            fields=[
                FormField(
                    multi_checkbox_field=MultiCheckboxField(
                        name='Preserved',
                        visual_region=BoxBounds(x=486, y=2163, width=282, height=99),
                        validator=MultiChoiceValidation.OPTIONAL,
                        checkboxes=[
                            MultiCheckboxOption(name='-20 C', region=BoxBounds(x=500, y=2182, width=18, height=18)),
                            MultiCheckboxOption(name='-80 C', region=BoxBounds(x=500, y=2232, width=18, height=18)),
                            MultiCheckboxOption(name='LN2', region=BoxBounds(x=636, y=2182, width=18, height=18)),
                            MultiCheckboxOption(name='Shield', region=BoxBounds(x=636, y=2232, width=18, height=18)),
                        ],
                        exporter=MultiCheckboxExporter(
                            export_field_name='Liver_pres',
                            export_type=MultiCbExportType.SINGLE_COLUMN,
                        ),
                    )
                ),
                FormField(
                    text_field=TextField(
                        name='Remarks',
                        visual_region=BoxBounds(x=940, y=2163, width=262, height=99),
                        exporters=[
                            TextExporter(export_field_name='L_remarks'),
                        ],
                    ),
                ),
            ],
        ),
        FieldGroup(
            name='Muscle',
            visual_region=BoxBounds(x=292, y=2271, width=909, height=99),
            fields=[
                FormField(
                    multi_checkbox_field=MultiCheckboxField(
                        name='Preserved',
                        visual_region=BoxBounds(x=486, y=2271, width=282, height=99),
                        validator=MultiChoiceValidation.OPTIONAL,
                        checkboxes=[
                            MultiCheckboxOption(name='-20 C', region=BoxBounds(x=500, y=2290, width=18, height=18)),
                            MultiCheckboxOption(name='-80 C', region=BoxBounds(x=500, y=2340, width=18, height=18)),
                            MultiCheckboxOption(name='LN2', region=BoxBounds(x=636, y=2290, width=18, height=18)),
                            MultiCheckboxOption(name='Shield', region=BoxBounds(x=636, y=2340, width=18, height=18)),
                        ],
                        exporter=MultiCheckboxExporter(
                            export_field_name='Muscle_pres',
                            export_type=MultiCbExportType.SINGLE_COLUMN,
                        ),
                    )
                ),
                FormField(
                    text_field=TextField(
                        name='Remarks',
                        visual_region=BoxBounds(x=940, y=2271, width=262, height=99),
                        exporters=[
                            TextExporter(export_field_name='M_remarks'),
                        ],
                    ),
                ),
            ],
        ),
        FieldGroup(
            name='GI / LI / colon',
            visual_region=BoxBounds(x=292, y=2379, width=909, height=99),
            fields=[
                FormField(
                    circled_field=CircledField(
                        name='Type',
                        visual_region=BoxBounds(x=292, y=2379, width=188, height=104),
                        validator=MultiChoiceValidation.MAXIMUM_ONE,
                        options=[
                            CircledOption(name='GI', region=BoxBounds(x=296, y=2384, width=66, height=48)),
                            CircledOption(name='LI', region=BoxBounds(x=380, y=2382, width=66, height=52)),
                            CircledOption(name='colon', region=BoxBounds(x=304, y=2426, width=138, height=56)),
                        ],
                        exporter=CircledExporter(
                            export_field_name='GI,LI,colon_coll'
                        ),
                    )
                ),
                FormField(
                    multi_checkbox_field=MultiCheckboxField(
                        name='Preserved',
                        visual_region=BoxBounds(x=486, y=2379, width=282, height=99),
                        validator=MultiChoiceValidation.OPTIONAL,
                        checkboxes=[
                            MultiCheckboxOption(name='-20 C', region=BoxBounds(x=500, y=2398, width=18, height=18)),
                            MultiCheckboxOption(name='10% form', region=BoxBounds(x=500, y=2448, width=18, height=18)),
                            MultiCheckboxOption(name='LN2', region=BoxBounds(x=636, y=2398, width=18, height=18)),
                            MultiCheckboxOption(name='Shield', region=BoxBounds(x=636, y=2448, width=18, height=18)),
                        ],
                        exporter=MultiCheckboxExporter(
                            export_field_name='GI/LI/C_pres',
                            export_type=MultiCbExportType.SINGLE_COLUMN,
                        ),
                    )
                ),
                FormField(
                    text_field=TextField(
                        name='Remarks',
                        visual_region=BoxBounds(x=940, y=2379, width=262, height=99),
                        exporters=[
                            TextExporter(export_field_name='GI/LI/C_remarks'),
                        ],
                    ),
                ),
            ],
        ),
        FieldGroup(
            name='Feces',
            visual_region=BoxBounds(x=292, y=2487, width=909, height=99),
            fields=[
                FormField(
                    multi_checkbox_field=MultiCheckboxField(
                        name='Preserved',
                        visual_region=BoxBounds(x=486, y=2487, width=282, height=99),
                        validator=MultiChoiceValidation.OPTIONAL,
                        checkboxes=[
                            MultiCheckboxOption(name='-20 C', region=BoxBounds(x=500, y=2506, width=18, height=18)),
                            MultiCheckboxOption(name='10% form', region=BoxBounds(x=500, y=2556, width=18, height=18)),
                            MultiCheckboxOption(name='LN2', region=BoxBounds(x=636, y=2506, width=18, height=18)),
                            MultiCheckboxOption(name='Shield', region=BoxBounds(x=636, y=2556, width=18, height=18)),
                        ],
                        exporter=MultiCheckboxExporter(
                            export_field_name='Feces_pres',
                            export_type=MultiCbExportType.SINGLE_COLUMN,
                        ),
                    )
                ),
                FormField(
                    text_field=TextField(
                        name='Remarks',
                        visual_region=BoxBounds(x=940, y=2487, width=262, height=99),
                        exporters=[
                            TextExporter(export_field_name='F_remarks'),
                        ],
                    ),
                ),
            ],
        ),
        FieldGroup(
            name='Blood',
            visual_region=BoxBounds(x=292, y=2595, width=909, height=99),
            fields=[
                FormField(
                    multi_checkbox_field=MultiCheckboxField(
                        name='Preserved',
                        visual_region=BoxBounds(x=486, y=2595, width=282, height=99),
                        validator=MultiChoiceValidation.OPTIONAL,
                        checkboxes=[
                            MultiCheckboxOption(name='Nobuto', region=BoxBounds(x=500, y=2614, width=18, height=18)),
                            MultiCheckboxOption(name='10% form', region=BoxBounds(x=496, y=2664, width=18, height=18)),
                            MultiCheckboxOption(name='LN2', region=BoxBounds(x=633, y=2614, width=18, height=18)),
                            MultiCheckboxOption(name='Shield', region=BoxBounds(x=636, y=2664, width=18, height=18)),
                        ],
                        exporter=MultiCheckboxExporter(
                            export_field_name='Blood_pres',
                            export_type=MultiCbExportType.SINGLE_COLUMN,
                        ),
                    )
                ),
                FormField(
                    text_field=TextField(
                        name='Remarks',
                        visual_region=BoxBounds(x=940, y=2595, width=262, height=99),
                        exporters=[
                            TextExporter(export_field_name='B_remarks'),
                        ],
                    ),
                ),
            ],
        ),
        FieldGroup(
            name='Ecto Parasites 1',
            visual_region=BoxBounds(x=1257, y=1952, width=1124, height=99),
            fields=[
                FormField(
                    multi_checkbox_field=MultiCheckboxField(
                        name='Type & Count',
                        visual_region=BoxBounds(x=1257, y=1952, width=346, height=99),
                        validator=MultiChoiceValidation.OPTIONAL,
                        checkboxes=[
                            MultiCheckboxOption(
                                name='Flea',
                                region=BoxBounds(x=1294, y=1965, width=36, height=30),
                                text_region=BoxBounds(x=1280, y=1958, width=69, height=39),
                            ),
                            MultiCheckboxOption(
                                name='Tick',
                                region=BoxBounds(x=1308, y=2013, width=22, height=26),
                                text_region=BoxBounds(x=1281, y=2001, width=69, height=39),
                            ),
                            MultiCheckboxOption(
                                name='Mite',
                                region=BoxBounds(x=1460, y=1966, width=24, height=27),
                                text_region=BoxBounds(x=1436, y=1958, width=69, height=39),
                            ),
                            MultiCheckboxOption(
                                name='Lice',
                                region=BoxBounds(x=1460, y=2012, width=24, height=26),
                                text_region=BoxBounds(x=1434, y=2001, width=69, height=39),
                            ),
                        ],
                        exporter=MultiCheckboxExporter(
                            export_field_name='ecto1_type',
                            export_type=MultiCbExportType.MULTI_USE_TEXT,
                        ),
                    )
                ),
                FormField(
                    multi_checkbox_field=MultiCheckboxField(
                        name='Preserved',
                        visual_region=BoxBounds(x=1610, y=1952, width=266, height=99),
                        validator=MultiChoiceValidation.OPTIONAL,
                        checkboxes=[
                            MultiCheckboxOption(name='80%', region=BoxBounds(x=1623, y=1971, width=18, height=18)),
                            MultiCheckboxOption(name='95%', region=BoxBounds(x=1742, y=1971, width=18, height=18)),
                            MultiCheckboxOption(name='LN2', region=BoxBounds(x=1623, y=2020, width=18, height=18)),
                            MultiCheckboxOption(name='Other', region=BoxBounds(x=1738, y=2020, width=18, height=18)),
                        ],
                        exporter=MultiCheckboxExporter(
                            export_field_name='ecto1_pres',
                            export_type=MultiCbExportType.SINGLE_COLUMN,
                        ),
                    )
                ),
                FormField(
                    text_field=TextField(
                        name='Remarks',
                        visual_region=BoxBounds(x=2054, y=1952, width=327, height=99),
                        exporters=[
                            TextExporter(export_field_name='ecto1_remarks'),
                        ],
                    ),
                ),
            ],
        ),
        FieldGroup(
            name='Ecto Parasites 2',
            visual_region=BoxBounds(x=1257, y=2056, width=1124, height=99),
            fields=[
                FormField(
                    multi_checkbox_field=MultiCheckboxField(
                        name='Type & Count',
                        visual_region=BoxBounds(x=1257, y=2056, width=346, height=99),
                        validator=MultiChoiceValidation.OPTIONAL,
                        checkboxes=[
                            MultiCheckboxOption(
                                name='Flea',
                                region=BoxBounds(x=1294, y=2070, width=36, height=30),
                                text_region=BoxBounds(x=1280, y=2062, width=69, height=39),
                            ),
                            MultiCheckboxOption(
                                name='Tick',
                                region=BoxBounds(x=1308, y=2118, width=22, height=26),
                                text_region=BoxBounds(x=1281, y=2106, width=69, height=39),
                            ),
                            MultiCheckboxOption(
                                name='Mite',
                                region=BoxBounds(x=1460, y=2072, width=24, height=27),
                                text_region=BoxBounds(x=1436, y=2062, width=69, height=39),
                            ),
                            MultiCheckboxOption(
                                name='Lice',
                                region=BoxBounds(x=1460, y=2116, width=24, height=26),
                                text_region=BoxBounds(x=1434, y=2106, width=69, height=39),
                            ),
                        ],
                        exporter=MultiCheckboxExporter(
                            export_field_name='ecto2_type',
                            export_type=MultiCbExportType.MULTI_USE_TEXT,
                        ),
                    )
                ),
                FormField(
                    multi_checkbox_field=MultiCheckboxField(
                        name='Preserved',
                        visual_region=BoxBounds(x=1610, y=2056, width=266, height=99),
                        validator=MultiChoiceValidation.OPTIONAL,
                        checkboxes=[
                            MultiCheckboxOption(name='80%', region=BoxBounds(x=1623, y=2076, width=18, height=18)),
                            MultiCheckboxOption(name='95%', region=BoxBounds(x=1742, y=2076, width=18, height=18)),
                            MultiCheckboxOption(name='LN2', region=BoxBounds(x=1623, y=2126, width=18, height=18)),
                            MultiCheckboxOption(name='Other', region=BoxBounds(x=1738, y=2126, width=18, height=18)),
                        ],
                        exporter=MultiCheckboxExporter(
                            export_field_name='ecto2_pres',
                            export_type=MultiCbExportType.SINGLE_COLUMN,
                        ),
                    )
                ),
                FormField(
                    text_field=TextField(
                        name='Remarks',
                        visual_region=BoxBounds(x=2054, y=2056, width=327, height=99),
                        exporters=[
                            TextExporter(export_field_name='ecto2_remarks'),
                        ],
                    ),
                ),
            ],
        ),
        FieldGroup(
            name='Misc Parasites',
            visual_region=BoxBounds(x=1252, y=2162, width=1131, height=108),
            fields=[
                FormField(
                    text_field=TextField(
                        name='Type',
                        visual_region=BoxBounds(x=1257, y=2163, width=346, height=104),
                        exporters=[
                            TextExporter(export_field_name='misc_para_type'),
                        ],
                    ),
                ),
                FormField(
                    text_field=TextField(
                        name='Count',
                        visual_region=BoxBounds(x=1257, y=2163, width=346, height=104),
                        exporters=[
                            TextExporter(export_field_name='misc_para_count'),
                        ],
                    ),
                ),
                FormField(
                    text_field=TextField(
                        name='Preserved',
                        visual_region=BoxBounds(x=1610, y=2163, width=266, height=104),
                        exporters=[
                            TextExporter(export_field_name='misc_para_pres'),
                        ],
                    ),
                ),
                FormField(
                    text_field=TextField(
                        name='Remarks',
                        visual_region=BoxBounds(x=2054, y=2163, width=327, height=104),
                        exporters=[
                            TextExporter(export_field_name='misc_para_remarks'),
                        ],
                    ),
                ),
            ],
        ),
        FieldGroup(
            name='Endo Parasites 1',
            visual_region=BoxBounds(x=1257, y=2271, width=1124, height=104),
            fields=[
                FormField(
                    multi_checkbox_field=MultiCheckboxField(
                        name='Type & Count',
                        visual_region=BoxBounds(x=1257, y=2271, width=346, height=104),
                        validator=MultiChoiceValidation.REQUIRE_ONE,
                        checkboxes=[
                            MultiCheckboxOption(
                                name='Nema',
                                region=BoxBounds(x=1284, y=2288, width=28, height=27),
                                text_region=BoxBounds(x=1263, y=2277, width=68, height=40),
                            ),
                            MultiCheckboxOption(
                                name='Trem',
                                region=BoxBounds(x=1287, y=2331, width=30, height=30),
                                text_region=BoxBounds(x=1264, y=2325, width=68, height=38),
                            ),
                            MultiCheckboxOption(
                                name='Cest',
                                region=BoxBounds(x=1470, y=2290, width=24, height=24),
                                text_region=BoxBounds(x=1446, y=2280, width=69, height=38),
                            ),
                            MultiCheckboxOption(
                                name='Cyst',
                                region=BoxBounds(x=1473, y=2334, width=24, height=26),
                                text_region=BoxBounds(x=1446, y=2326, width=69, height=36),
                            ),
                        ],
                        exporter=MultiCheckboxExporter(
                            export_field_name='endo1_type',
                            export_type=MultiCbExportType.MULTI_USE_TEXT,
                        ),
                    )
                ),
                FormField(
                    multi_checkbox_field=MultiCheckboxField(
                        name='Preserved',
                        visual_region=BoxBounds(x=1610, y=2271, width=266, height=104),
                        validator=MultiChoiceValidation.REQUIRE_ONE,
                        checkboxes=[
                            MultiCheckboxOption(name='80%', region=BoxBounds(x=1623, y=2290, width=18, height=18)),
                            MultiCheckboxOption(name='LN2', region=BoxBounds(x=1623, y=2340, width=18, height=18)),
                            MultiCheckboxOption(name='Other', region=BoxBounds(x=1752, y=2290, width=18, height=18)),
                        ],
                        exporter=MultiCheckboxExporter(
                            export_field_name='endo1_pres',
                            export_type=MultiCbExportType.SINGLE_COLUMN,
                        ),
                    )
                ),
                FormField(
                    text_field=TextField(
                        name='Remarks',
                        visual_region=BoxBounds(x=2054, y=2271, width=327, height=104),
                        exporters=[
                            TextExporter(export_field_name='endo1_remarks'),
                        ],
                    ),
                ),
            ],
        ),
        FieldGroup(
            name='Endo Parasites 2',
            visual_region=BoxBounds(x=1257, y=2379, width=1124, height=104),
            fields=[
                FormField(
                    multi_checkbox_field=MultiCheckboxField(
                        name='Type & Count',
                        visual_region=BoxBounds(x=1257, y=2379, width=346, height=104),
                        validator=MultiChoiceValidation.REQUIRE_ONE,
                        checkboxes=[
                            MultiCheckboxOption(
                                name='Nema',
                                region=BoxBounds(x=1284, y=2397, width=28, height=27),
                                text_region=BoxBounds(x=1263, y=2385, width=68, height=40),
                            ),
                            MultiCheckboxOption(
                                name='Trem',
                                region=BoxBounds(x=1287, y=2439, width=30, height=30),
                                text_region=BoxBounds(x=1264, y=2433, width=68, height=38),
                            ),
                            MultiCheckboxOption(
                                name='Cest',
                                region=BoxBounds(x=1470, y=2398, width=24, height=24),
                                text_region=BoxBounds(x=1446, y=2388, width=69, height=38),
                            ),
                            MultiCheckboxOption(
                                name='Cyst',
                                region=BoxBounds(x=1473, y=2442, width=24, height=26),
                                text_region=BoxBounds(x=1446, y=2434, width=69, height=36),
                            ),
                        ],
                        exporter=MultiCheckboxExporter(
                            export_field_name='endo2_type',
                            export_type=MultiCbExportType.MULTI_USE_TEXT,
                        ),
                    )
                ),
                FormField(
                    multi_checkbox_field=MultiCheckboxField(
                        name='Preserved',
                        visual_region=BoxBounds(x=1610, y=2379, width=266, height=104),
                        validator=MultiChoiceValidation.REQUIRE_ONE,
                        checkboxes=[
                            MultiCheckboxOption(name='80%', region=BoxBounds(x=1623, y=2398, width=18, height=18)),
                            MultiCheckboxOption(name='LN2', region=BoxBounds(x=1623, y=2448, width=18, height=18)),
                            MultiCheckboxOption(name='Other', region=BoxBounds(x=1752, y=2398, width=18, height=18)),
                        ],
                        exporter=MultiCheckboxExporter(
                            export_field_name='endo2_pres',
                            export_type=MultiCbExportType.SINGLE_COLUMN,
                        ),
                    )
                ),
                FormField(
                    text_field=TextField(
                        name='Remarks',
                        visual_region=BoxBounds(x=2054, y=2379, width=327, height=104),
                        exporters=[
                            TextExporter(export_field_name='endo2_remarks'),
                        ],
                    ),
                ),
            ],
        ),
        FieldGroup(
            name='Endo Parasites 3',
            visual_region=BoxBounds(x=1257, y=2487, width=1124, height=104),
            fields=[
                FormField(
                    multi_checkbox_field=MultiCheckboxField(
                        name='Type & Count',
                        visual_region=BoxBounds(x=1257, y=2487, width=346, height=104),
                        validator=MultiChoiceValidation.REQUIRE_ONE,
                        checkboxes=[
                            MultiCheckboxOption(
                                name='Nema',
                                region=BoxBounds(x=1284, y=2505, width=28, height=27),
                                text_region=BoxBounds(x=1263, y=2493, width=68, height=40),
                            ),
                            MultiCheckboxOption(
                                name='Trem',
                                region=BoxBounds(x=1287, y=2547, width=30, height=30),
                                text_region=BoxBounds(x=1264, y=2541, width=68, height=38),
                            ),
                            MultiCheckboxOption(
                                name='Cest',
                                region=BoxBounds(x=1470, y=2506, width=24, height=24),
                                text_region=BoxBounds(x=1446, y=2496, width=69, height=38),
                            ),
                            MultiCheckboxOption(
                                name='Cyst',
                                region=BoxBounds(x=1473, y=2550, width=24, height=26),
                                text_region=BoxBounds(x=1446, y=2542, width=69, height=36),
                            ),
                        ],
                        exporter=MultiCheckboxExporter(
                            export_field_name='endo3_type',
                            export_type=MultiCbExportType.MULTI_USE_TEXT,
                        ),
                    )
                ),
                FormField(
                    multi_checkbox_field=MultiCheckboxField(
                        name='Preserved',
                        visual_region=BoxBounds(x=1610, y=2487, width=266, height=104),
                        validator=MultiChoiceValidation.REQUIRE_ONE,
                        checkboxes=[
                            MultiCheckboxOption(name='80%', region=BoxBounds(x=1623, y=2506, width=18, height=18)),
                            MultiCheckboxOption(name='LN2', region=BoxBounds(x=1623, y=2556, width=18, height=18)),
                            MultiCheckboxOption(name='Other', region=BoxBounds(x=1752, y=2506, width=18, height=18)),
                        ],
                        exporter=MultiCheckboxExporter(
                            export_field_name='endo3_pres',
                            export_type=MultiCbExportType.SINGLE_COLUMN,
                        ),
                    )
                ),
                FormField(
                    text_field=TextField(
                        name='Remarks',
                        visual_region=BoxBounds(x=2054, y=2487, width=327, height=104),
                        exporters=[
                            TextExporter(export_field_name='endo3_remarks'),
                        ],
                    ),
                ),
            ],
        ),
        FieldGroup(
            name='Embryos',
            visual_region=BoxBounds(x=1257, y=2595, width=1124, height=104),
            fields=[
                FormField(
                    text_field=TextField(
                        name='Count',
                        visual_region=BoxBounds(x=1308, y=2625, width=68, height=39),
                        text_validator=TextValidator(datatype=TextValidatorDatatype.INTEGER),
                        exporters=[
                            TextExporter(export_field_name='emb_count'),
                        ],
                    ),
                ),
                FormField(
                    multi_checkbox_field=MultiCheckboxField(
                        name='Preserved',
                        visual_region=BoxBounds(x=1610, y=2595, width=266, height=104),
                        validator=MultiChoiceValidation.OPTIONAL,
                        checkboxes=[
                            MultiCheckboxOption(name='10% form', region=BoxBounds(x=1623, y=2614, width=18, height=18)),
                            MultiCheckboxOption(name='LN2', region=BoxBounds(x=1623, y=2664, width=18, height=18)),
                            MultiCheckboxOption(name='95%', region=BoxBounds(x=1755, y=2614, width=18, height=18)),
                            MultiCheckboxOption(name='Shield', region=BoxBounds(x=1738, y=2664, width=18, height=18)),
                        ],
                        exporter=MultiCheckboxExporter(
                            export_field_name='emb_pres',
                            export_type=MultiCbExportType.SINGLE_COLUMN,
                        ),
                    )
                ),
                FormField(
                    text_field=TextField(
                        name='Remarks',
                        visual_region=BoxBounds(x=2054, y=2595, width=327, height=104),
                        exporters=[
                            TextExporter(export_field_name='emb_remarks'),
                        ],
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
                        visual_region=BoxBounds(x=558, y=2704, width=693, height=58),
                        validator=MultiChoiceValidation.REQUIRE_ONE,
                        checkboxes=[
                            MultiCheckboxOption(name='Excellent', region=BoxBounds(x=572, y=2733, width=14, height=14)),
                            MultiCheckboxOption(name='Very Good', region=BoxBounds(x=741, y=2733, width=14, height=14)),
                            MultiCheckboxOption(name='Good', region=BoxBounds(x=930, y=2733, width=14, height=14)),
                            MultiCheckboxOption(name='Fair', region=BoxBounds(x=1052, y=2733, width=14, height=14)),
                            MultiCheckboxOption(name='Poor', region=BoxBounds(x=1150, y=2733, width=14, height=14)),
                        ],
                        exporter=MultiCheckboxExporter(
                            export_field_name='tiss_quality',
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
                        name='Time of Death',
                        visual_region=BoxBounds(x=574, y=2757, width=194, height=56),
                        text_validator=TextValidator(
                            datatype=TextValidatorDatatype.TIME,
                        ),
                        exporters=[
                            TextExporter(export_field_name='time_death'),
                        ],
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
                        visual_region=BoxBounds(x=1160, y=2757, width=171, height=56),
                        text_validator=TextValidator(datatype=TextValidatorDatatype.TIME),
                        exporters=[
                            TextExporter(export_field_name='time_tissue_pres'),
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
                        name='Elapsed Time (min)',
                        visual_region=BoxBounds(x=574, y=2823, width=192, height=54),
                        text_validator=TextValidator(
                            datatype=TextValidatorDatatype.INTEGER,
                        ),
                        exporters=[
                            TextExporter(export_field_name='time_elapsed(min)'),
                        ],
                    )
                ),
            ],
        ),
        FieldGroup(
            name='Cold Chain Progression',
            visual_region=BoxBounds(x=1354, y=2751, width=1022, height=135),
            fields=[
                FormField(
                    text_field=TextField(
                        name='Dry Ice',
                        visual_region=BoxBounds(x=1380, y=2760, width=222, height=57),
                        text_validator=TextValidator(datatype=TextValidatorDatatype.DATE),
                        exporters=[
                            TextExporter(export_field_name='date_dryice', capitalization=CapitalizationType.TITLE),
                        ],
                    )
                ),
                FormField(
                    text_field=TextField(
                        name='Field LN2',
                        visual_region=BoxBounds(x=1734, y=2754, width=214, height=63),
                        text_validator=TextValidator(datatype=TextValidatorDatatype.DATE),
                        exporters=[
                            TextExporter(export_field_name='date_fieldLN2', capitalization=CapitalizationType.TITLE),
                        ],
                    )
                ),
                FormField(
                    text_field=TextField(
                        name='-20 C',
                        visual_region=BoxBounds(x=2061, y=2752, width=220, height=64),
                        text_validator=TextValidator(datatype=TextValidatorDatatype.DATE),
                        exporters=[
                            TextExporter(export_field_name='date_-20C', capitalization=CapitalizationType.TITLE),
                        ],
                    )
                ),
                FormField(
                    text_field=TextField(
                        name='-40 C',
                        visual_region=BoxBounds(x=1384, y=2822, width=213, height=62),
                        text_validator=TextValidator(datatype=TextValidatorDatatype.DATE),
                        exporters=[
                            TextExporter(export_field_name='date_-40C', capitalization=CapitalizationType.TITLE),
                        ],
                    )
                ),
                FormField(
                    text_field=TextField(
                        name='-80 C',
                        visual_region=BoxBounds(x=1738, y=2823, width=212, height=60),
                        text_validator=TextValidator(datatype=TextValidatorDatatype.DATE),
                        exporters=[
                            TextExporter(export_field_name='date_-80C', capitalization=CapitalizationType.TITLE),
                        ],
                    )
                ),
                FormField(
                    text_field=TextField(
                        name='Install LN2',
                        visual_region=BoxBounds(x=2066, y=2822, width=216, height=62),
                        text_validator=TextValidator(datatype=TextValidatorDatatype.DATE),
                        exporters=[
                            TextExporter(export_field_name='date_installLN2', capitalization=CapitalizationType.TITLE),
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
                        visual_region=BoxBounds(x=285, y=2896, width=2100, height=206),
                        text_regions=[
                            BoxBounds(x=826, y=2901, width=1545, height=52),
                            BoxBounds(x=292, y=2956, width=2074, height=62),
                            BoxBounds(x=288, y=3026, width=2085, height=58),
                        ],
                        exporters=[
                            TextExporter(export_field_name='remarks_general', capitalization=CapitalizationType.NONE),
                        ],
                    )
                ),
            ],
        ),
    ]

    session.add(form)
    session.commit()
