from .util import OcrField, BoxBounds


TOP_OCR_FIELDS = [
    # Header
    OcrField(name='KT Number', region=BoxBounds(x=248, y=140, width=125, height=37), segment='7'),
    OcrField(name='Prep Number', region=BoxBounds(x=452, y=135, width=205, height=37), segment='7'),
    OcrField(name='KU Number', region=BoxBounds(x=724, y=128, width=205, height=44), segment='7'),
    OcrField(name='OT Number', region=BoxBounds(x=993, y=128, width=200, height=44), segment='7'),

    # Body
    OcrField(name='Locality', region=BoxBounds(x=281, y=191, width=804, height=31), segment='7'),

    OcrField(name='Latitude', region=BoxBounds(x=245, y=227, width=234, height=33), segment='7'),
    OcrField(name='Longitude', region=BoxBounds(x=550, y=228, width=236, height=32), segment='7'),
    OcrField(name='Source', region=BoxBounds(x=869, y=227, width=199, height=33), segment='7'),
    OcrField(name='Error', region=BoxBounds(x=1168, y=223, width=113, height=37), segment='7'),

    OcrField(name='Species', region=BoxBounds(x=287, y=267, width=686, height=31), segment='7'),
    OcrField(name='GPS Waypoint', region=BoxBounds(x=1075, y=264, width=203, height=34), segment='7'),

    OcrField(name='Habitat', region=BoxBounds(x=248, y=303, width=1026, height=35), segment='7'),

    OcrField(name='Collection Date', region=BoxBounds(x=301, y=339, width=433, height=35), segment='7'),
    OcrField(name='Collector', region=BoxBounds(x=837, y=338, width=431, height=35), segment='7'),

    OcrField(name='Prep Date', region=BoxBounds(x=311, y=376, width=419, height=35), segment='7'),
    OcrField(name='Preparator', region=BoxBounds(x=849, y=376, width=421, height=35), segment='7'),
]
