from .util import OcrField, BoxBounds


FORM1_OCR_FIELDS = [
    # OcrField(name='KT #', region=BoxBounds(x=248, y=140, width=125, height=37), segment='7'),
    OcrField(name='Locality', region=BoxBounds(x=281, y=191, width=804, height=31), segment='7'),
    # OcrField(name='Species', region=BoxBounds(x=287, y=267, width=686, height=31), segment='7'),
    # OcrField(name='Habitat', region=BoxBounds(x=248, y=303, width=1026, height=35), segment='7'),
    # OcrField(name='Collection Date', region=BoxBounds(x=301, y=339, width=433, height=33), segment='7'),
]
