from src.validation.multi_checkbox import OptionalCheckboxes, RequireOneCheckboxes
from src.validation.single_checkbox import OptionalCheckbox
from src.validation.text import TextOptional, TextRequired, KtNumber, PrepNumber, Locality, GpsPoint, Date, Time, \
    Number, OtNumber, Initials, Tissues, TextValidationBypass

from .base_fields import TextField, MultilineTextField, MultiCheckboxOption, MultiCheckboxField, \
    CheckboxField, create_field_with_offset
from .util import BoxBounds

TOP_REGION = [
    TextField(name='KT Number', visual_region=BoxBounds(x=194, y=55, width=126, height=43), validator=KtNumber),
    TextField(name='Prep Number', visual_region=BoxBounds(x=395, y=55, width=208, height=45), validator=PrepNumber),
    TextField(name='KU Number', visual_region=BoxBounds(x=661, y=53, width=207, height=47), validator=Number),
    TextField(name='OT Number', visual_region=BoxBounds(x=928, y=54, width=200, height=46), validator=OtNumber),

    TextField(name='Locality', visual_region=BoxBounds(x=204, y=119, width=975, height=40), allow_copy=True, validator=Locality),

    MultiCheckboxField(
        name='Collection Method',
        visual_region=BoxBounds(x=117, y=166, width=1062, height=40),
        validator=RequireOneCheckboxes,
        checkboxes=[
            MultiCheckboxOption(name='Shot', region=BoxBounds(x=261, y=179, width=13, height=12)),
            MultiCheckboxOption(name='Net/Trap', region=BoxBounds(x=344, y=179, width=13, height=12)),
            MultiCheckboxOption(name='Salvage', region=BoxBounds(x=473, y=179, width=13, height=12)),
            MultiCheckboxOption(name='Unknown', region=BoxBounds(x=590, y=179, width=13, height=12)),
            MultiCheckboxOption(
                name='Other',
                region=BoxBounds(x=673, y=179, width=13, height=12),
                text_region=BoxBounds(x=756, y=164, width=421, height=33),
            ),
        ],
    ),

    # TextField(
    #     name='Iris',
    #     visual_region=BoxBounds(x=157, y=413, width=379, height=40),
    #     allow_copy=True,
    #     validator=TextRequired,
    #     text_region=BoxBounds(x=287, y=411, width=247, height=32),
    #     checkbox_region=BoxBounds(x=213, y=424, width=13, height=13),
    #     checkbox_text='dark brown',
    # ),
    # TextField(name='Time of Death', visual_region=BoxBounds(x=637, y=484, width=161, height=33), validator=Time),
    # TextField(
    #     name='Time of Tissue Preservation',
    #     visual_region=BoxBounds(x=797, y=485, width=423, height=40),
    #     validator=Time,
    #     text_region=BoxBounds(x=988, y=486, width=154, height=31),
    #     checkbox_region=BoxBounds(x=1150, y=498, width=13, height=13),
    #     checkbox_text='unknown',
    # ),
    #
    # TextField(name='Tissues', visual_region=BoxBounds(x=251, y=520, width=147, height=35), validator=Tissues),
    # TextField(name='No. Tubes', visual_region=BoxBounds(x=509, y=523, width=56, height=32), validator=Number),
    # MultiCheckboxField(
    #     name='Tissue Preservation',
    #     visual_region=BoxBounds(x=569, y=527, width=669, height=33),
    #     validator=RequireOneCheckboxes,
    #     checkboxes=[
    #         MultiCheckboxOption(name='-20 C', region=BoxBounds(x=693, y=536, width=13, height=13)),
    #         MultiCheckboxOption(name='-80 C', region=BoxBounds(x=791, y=536, width=13, height=13)),
    #         MultiCheckboxOption(name='LN2', region=BoxBounds(x=889, y=536, width=13, height=13)),
    #         MultiCheckboxOption(name='Ethanol', region=BoxBounds(x=970, y=536, width=13, height=13)),
    #         MultiCheckboxOption(
    #             name='Other',
    #             region=BoxBounds(x=1065, y=536, width=13, height=13),
    #             text_region=BoxBounds(x=1145, y=526, width=84, height=29),
    #         ),
    #     ],
    # ),
    #
    # MultilineTextField(
    #     name='Remarks',
    #     visual_region=BoxBounds(x=160, y=824, width=1067, height=73),
    #     validator=TextValidationBypass,
    #     line_regions=[
    #         BoxBounds(x=265, y=816, width=962, height=35),
    #         BoxBounds(x=162, y=856, width=937, height=32)
    #     ],
    # ),
    # CheckboxField(
    #     name='See Back',
    #     visual_region=BoxBounds(x=1095, y=855, width=133, height=40),
    #     validator=OptionalCheckbox,
    #     checkbox_region=BoxBounds(x=1104, y=869, width=13, height=13),
    # ),
]

BOTTOM_HALF_Y_OFFSET = 842
BOTTOM_HALF_FIELDS = [create_field_with_offset(field, BOTTOM_HALF_Y_OFFSET) for field in TOP_REGION]

ALL_REGIONS = {'top': TOP_REGION, 'bottom': BOTTOM_HALF_FIELDS}
