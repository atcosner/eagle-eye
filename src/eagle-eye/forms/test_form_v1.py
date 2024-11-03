from ..validation.multi_checkbox import  RequireOneCheckbox
from ..validation.single_checkbox import OptionalCheckbox
from ..validation.text import TextRequired, KtNumber, PrepNumber, Locality, Time, IntegerOrFloat, Tissues, \
    TextValidationBypass

from ..definitions.base_fields import TextField, MultilineTextField, MultiCheckboxOption, MultiCheckboxField, \
    CheckboxField, create_field_with_offset
from ..definitions.util import BoxBounds

TOP_REGION = [
    TextField(name='KT Number', visual_region=BoxBounds(x=194, y=55, width=126, height=43), validator=KtNumber),
    TextField(name='Prep Number', visual_region=BoxBounds(x=395, y=55, width=208, height=45), validator=PrepNumber),
    TextField(name='KU Number', visual_region=BoxBounds(x=661, y=53, width=207, height=47), validator=TextValidationBypass),
    TextField(name='OT Number', visual_region=BoxBounds(x=928, y=54, width=200, height=46), validator=TextValidationBypass),

    TextField(name='Locality', visual_region=BoxBounds(x=204, y=119, width=975, height=40), allow_copy=True, validator=Locality),

    MultiCheckboxField(
        name='Collection Method',
        visual_region=BoxBounds(x=117, y=166, width=1062, height=40),
        validator=RequireOneCheckbox,
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

    TextField(
        name='Iris',
        visual_region=BoxBounds(x=112, y=198, width=336, height=50),
        allow_copy=True,
        validator=TextRequired,
        text_region=BoxBounds(x=241, y=202, width=208, height=32),
        checkbox_region=BoxBounds(x=166, y=216, width=13, height=13),
        checkbox_text='dark brown',
    ),
    TextField(name='Time of Death', visual_region=BoxBounds(x=591, y=198, width=163, height=36), validator=Time),
    TextField(
        name='Time of Tissue Preservation',
        visual_region=BoxBounds(x=755, y=202, width=427, height=43),
        validator=Time,
        text_region=BoxBounds(x=940, y=201, width=159, height=33),
        checkbox_region=BoxBounds(x=1105, y=216, width=13, height=13),
        checkbox_text='unknown',
    ),

    TextField(name='Tissues', visual_region=BoxBounds(x=201, y=238, width=154, height=34), validator=Tissues),
    TextField(name='No. Tubes', visual_region=BoxBounds(x=459, y=236, width=64, height=36), validator=IntegerOrFloat),
    MultiCheckboxField(
        name='Tissue Preservation',
        visual_region=BoxBounds(x=525, y=240, width=660, height=40),
        validator=RequireOneCheckbox,
        checkboxes=[
            MultiCheckboxOption(name='-20 C', region=BoxBounds(x=646, y=254, width=12, height=12)),
            MultiCheckboxOption(name='-80 C', region=BoxBounds(x=744, y=254, width=12, height=12)),
            MultiCheckboxOption(name='LN2', region=BoxBounds(x=842, y=254, width=12, height=12)),
            MultiCheckboxOption(name='Ethanol', region=BoxBounds(x=923, y=254, width=13, height=12)),
            MultiCheckboxOption(
                name='Other',
                region=BoxBounds(x=1018, y=254, width=13, height=12),
                text_region=BoxBounds(x=1098, y=238, width=82, height=34),
            ),
        ],
    ),

    MultilineTextField(
        name='Remarks',
        visual_region=BoxBounds(x=111, y=279, width=1067, height=82),
        validator=TextValidationBypass,
        line_regions=[
            BoxBounds(x=217, y=276, width=960, height=33),
            BoxBounds(x=116, y=312, width=932, height=34),
        ],
    ),
    CheckboxField(
        name='See Back',
        visual_region=BoxBounds(x=1047, y=316, width=131, height=36),
        validator=OptionalCheckbox,
        checkbox_region=BoxBounds(x=1057, y=328, width=13, height=13),
    ),
]

BOTTOM_HALF_Y_OFFSET = 354
BOTTOM_HALF_FIELDS = [create_field_with_offset(field, BOTTOM_HALF_Y_OFFSET) for field in TOP_REGION]

ALL_REGIONS = {'top': TOP_REGION, 'bottom': BOTTOM_HALF_FIELDS}
