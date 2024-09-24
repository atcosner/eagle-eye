from src.validation.base import NoValidation
from src.validation.multi_checkbox import OptionalCheckboxes, RequireOneCheckboxes
from src.validation.single_checkbox import OptionalCheckbox
from src.validation.text import TextOptional, TextRequired, KtNumber, PrepNumber, Locality, GpsPoint, Date, Time, \
    Number, OtNumber, Initials, Tissues

from .base_fields import TextField, MultilineTextField, TextOrCheckboxField, MultiCheckboxOption, MultiCheckboxField, \
    CheckboxField, create_field_with_offset
from .util import BoxBounds

TOP_REGION = [
    TextField(name='KT Number', visual_region=BoxBounds(x=248, y=120, width=120, height=44), validator=KtNumber),
    TextField(name='Prep Number', visual_region=BoxBounds(x=441, y=120, width=207, height=46), validator=PrepNumber),
    TextField(name='KU Number', visual_region=BoxBounds(x=707, y=120, width=207, height=46), validator=Number),
    TextField(name='OT Number', visual_region=BoxBounds(x=972, y=120, width=215, height=46), validator=OtNumber),

    TextField(name='Locality', visual_region=BoxBounds(x=249, y=183, width=992, height=39), allow_copy=True, validator=Locality),

    TextField(name='Latitude', visual_region=BoxBounds(x=210, y=227, width=250, height=31), validator=GpsPoint),
    TextField(name='Longitude', visual_region=BoxBounds(x=511, y=225, width=253, height=33), validator=GpsPoint),
    TextField(name='GPS Waypoint', visual_region=BoxBounds(x=860, y=224, width=164, height=34), allow_copy=True, validator=TextOptional),
    TextField(name='Error (m)', visual_region=BoxBounds(x=1120, y=225, width=108, height=33), validator=TextOptional),

    TextField(name='Species', visual_region=BoxBounds(x=253, y=262, width=594, height=33), allow_copy=True, validator=NoValidation),
    TextField(name='Coordinate Source', visual_region=BoxBounds(x=997, y=262, width=235, height=33), allow_copy=True, validator=TextOptional),

    TextField(name='Collection Date', visual_region=BoxBounds(x=274, y=300, width=411, height=32), allow_copy=True, validator=Date),
    TextField(name='Collector', visual_region=BoxBounds(x=790, y=299, width=435, height=33), allow_copy=True, validator=Initials),

    TextField(name='Habitat', visual_region=BoxBounds(x=217, y=336, width=1012, height=32), allow_copy=True, validator=TextRequired),

    MultiCheckboxField(
        name='Collection Method',
        visual_region=BoxBounds(x=163, y=376, width=1061, height=35),
        validator=RequireOneCheckboxes,
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

    TextOrCheckboxField(
        name='Iris',
        visual_region=BoxBounds(x=157, y=413, width=379, height=40),
        validator=TextRequired,
        text_region=BoxBounds(x=287, y=411, width=247, height=32),
        checkbox_region=BoxBounds(x=213, y=424, width=13, height=13),
        checkbox_text='dark brown',
        # TODO: Allow this to be copied
    ),
    TextField(name='Bill', visual_region=BoxBounds(x=577, y=412, width=648, height=31), allow_copy=True, validator=TextOptional),

    TextField(name='Feet/Legs', visual_region=BoxBounds(x=242, y=450, width=726, height=30), allow_copy=True, validator=TextOptional),
    TextField(name='Weight (g)', visual_region=BoxBounds(x=1035, y=447, width=190, height=33), validator=Number),

    MultiCheckboxField(
        name='Tissue Date',
        visual_region=BoxBounds(x=160, y=488, width=283, height=35),
        validator=RequireOneCheckboxes,
        checkboxes=[
            MultiCheckboxOption(name='Collection', region=BoxBounds(x=280, y=498, width=13, height=13)),
            MultiCheckboxOption(name='Preparation', region=BoxBounds(x=360, y=498, width=13, height=13)),
        ],
    ),
    TextField(name='Time of Death', visual_region=BoxBounds(x=637, y=484, width=161, height=33), validator=Time),
    TextOrCheckboxField(
        name='Time of Tissue Preservation',
        visual_region=BoxBounds(x=797, y=485, width=423, height=40),
        validator=Time,
        text_region=BoxBounds(x=988, y=486, width=154, height=31),
        checkbox_region=BoxBounds(x=1150, y=498, width=13, height=13),
        checkbox_text='unknown',
    ),

    TextField(name='Tissues', visual_region=BoxBounds(x=251, y=520, width=147, height=35), validator=Tissues),
    TextField(name='No. Tubes', visual_region=BoxBounds(x=509, y=523, width=56, height=32), validator=Number),
    MultiCheckboxField(
        name='Tissue Preservation',
        visual_region=BoxBounds(x=569, y=527, width=669, height=33),
        validator=RequireOneCheckboxes,
        checkboxes=[
            MultiCheckboxOption(name='-20 C', region=BoxBounds(x=693, y=536, width=13, height=13)),
            MultiCheckboxOption(name='-80 C', region=BoxBounds(x=791, y=536, width=13, height=13)),
            MultiCheckboxOption(name='LN2', region=BoxBounds(x=889, y=536, width=13, height=13)),
            MultiCheckboxOption(name='Ethanol', region=BoxBounds(x=970, y=536, width=13, height=13)),
            MultiCheckboxOption(
                name='Other',
                region=BoxBounds(x=1065, y=536, width=13, height=13),
                text_region=BoxBounds(x=1145, y=526, width=84, height=29),
            ),
        ],
    ),

    TextField(name='Prep Date', visual_region=BoxBounds(x=279, y=560, width=378, height=32), validator=Date),
    TextField(name='Preparator', visual_region=BoxBounds(x=776, y=562, width=451, height=30), validator=Initials),

    MultiCheckboxField(
        name='Preps',
        visual_region=BoxBounds(x=158, y=600, width=1077, height=36),
        validator=RequireOneCheckboxes,
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
    ),

    TextField(name='Molt', visual_region=BoxBounds(x=220, y=634, width=1004, height=32), validator=TextRequired),

    TextField(name='Gonads', visual_region=BoxBounds(x=255, y=671, width=967, height=31), validator=TextRequired),

    TextField(name='Skull', visual_region=BoxBounds(x=222, y=706, width=257, height=34), validator=TextRequired),
    MultiCheckboxField(
        name='Fat',
        visual_region=BoxBounds(x=479, y=706, width=384, height=41),
        validator=RequireOneCheckboxes,
        checkboxes=[
            MultiCheckboxOption(name='None', region=BoxBounds(x=536, y=721, width=13, height=13)),
            MultiCheckboxOption(name='Light', region=BoxBounds(x=599, y=721, width=13, height=13)),
            MultiCheckboxOption(name='Medium', region=BoxBounds(x=658, y=721, width=13, height=13)),
            MultiCheckboxOption(name='Heavy', region=BoxBounds(x=724, y=721, width=13, height=13)),
            MultiCheckboxOption(name='Very Heavy', region=BoxBounds(x=787, y=721, width=13, height=13)),
        ],
    ),
    TextField(name='Bursa', visual_region=BoxBounds(x=980, y=709, width=243, height=31), validator=TextRequired),

    TextField(name='Stomach', visual_region=BoxBounds(x=232, y=745, width=992, height=32), validator=TextRequired),

    MultiCheckboxField(
        name='Sex',
        visual_region=BoxBounds(x=162, y=786, width=329, height=31),
        validator=RequireOneCheckboxes,
        checkboxes=[
            MultiCheckboxOption(name='Female', region=BoxBounds(x=222, y=795, width=13, height=13)),
            MultiCheckboxOption(name='Male', region=BoxBounds(x=329, y=795, width=13, height=13)),
            MultiCheckboxOption(name='Unknown', region=BoxBounds(x=418, y=795, width=13, height=13)),
        ],
    ),
    TextField(name='Age', visual_region=BoxBounds(x=579, y=783, width=315, height=31), validator=TextRequired),
    MultiCheckboxField(
        name='Parasites Collected',
        visual_region=BoxBounds(x=895, y=787, width=333, height=29),
        validator=OptionalCheckboxes,
        checkboxes=[
            MultiCheckboxOption(name='Ecto', region=BoxBounds(x=1054, y=795, width=13, height=13)),
            MultiCheckboxOption(name='Endo', region=BoxBounds(x=1143, y=795, width=13, height=13)),
        ],
    ),

    MultilineTextField(
        name='Remarks',
        visual_region=BoxBounds(x=160, y=824, width=1067, height=73),
        validator=TextOptional,
        line_regions=[
            BoxBounds(x=265, y=816, width=962, height=35),
            BoxBounds(x=162, y=856, width=937, height=32)
        ],
    ),
    CheckboxField(
        name='See Back',
        visual_region=BoxBounds(x=1095, y=855, width=133, height=40),
        validator=OptionalCheckbox,
        checkbox_region=BoxBounds(x=1104, y=869, width=13, height=13),
    ),

    MultiCheckboxField(
        name='Photos',
        visual_region=BoxBounds(x=162, y=898, width=259, height=35),
        validator=OptionalCheckboxes,
        checkboxes=[
            MultiCheckboxOption(name='Habitat', region=BoxBounds(x=253, y=907, width=13, height=13)),
            MultiCheckboxOption(name='Specimen', region=BoxBounds(x=334, y=907, width=13, height=13)),
        ],
    ),
    CheckboxField(
        name='Audio',
        visual_region=BoxBounds(x=471, y=899, width=93, height=30),
        validator=OptionalCheckbox,
        checkbox_region=BoxBounds(x=479, y=907, width=13, height=13),
    ),
    MultiCheckboxField(
        name='Parasite Presence',
        visual_region=BoxBounds(x=612, y=897, width=408, height=33),
        validator=OptionalCheckboxes,
        checkboxes=[
            MultiCheckboxOption(name='70%', region=BoxBounds(x=773, y=907, width=13, height=13)),
            MultiCheckboxOption(name='80%', region=BoxBounds(x=858, y=907, width=13, height=13)),
            MultiCheckboxOption(name='95%', region=BoxBounds(x=944, y=907, width=13, height=13)),
        ],
    ),
    CheckboxField(
        name='Washed',
        visual_region=BoxBounds(x=1067, y=898, width=119, height=31),
        validator=OptionalCheckbox,
        checkbox_region=BoxBounds(x=1076, y=907, width=13, height=13)
    ),
]

BOTTOM_HALF_Y_OFFSET = 842
BOTTOM_HALF_FIELDS = [create_field_with_offset(field, BOTTOM_HALF_Y_OFFSET) for field in TOP_REGION]

ALL_REGIONS = {'top': TOP_REGION, 'bottom': BOTTOM_HALF_FIELDS}
