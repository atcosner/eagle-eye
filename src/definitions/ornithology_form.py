from .util import OcrField, BoxBounds


TOP_OCR_FIELDS = [
    # Header
    OcrField(name='KT Number', region=BoxBounds(x=242, y=127, width=126, height=46), segment='7'),
    OcrField(name='Prep Number', region=BoxBounds(x=441, y=126, width=209, height=45), segment='7'),
    OcrField(name='KU Number', region=BoxBounds(x=708, y=125, width=201, height=46), segment='7'),
    OcrField(name='OT Number', region=BoxBounds(x=966, y=125, width=221, height=46), segment='7'),

    # Body
    OcrField(name='Locality', region=BoxBounds(x=277, y=187, width=783, height=32), segment='7'),

    OcrField(name='Latitude', region=BoxBounds(x=237, y=223, width=235, height=32), segment='7'),
    OcrField(name='Longitude', region=BoxBounds(x=534, y=221, width=235, height=34), segment='7'),
    OcrField(name='Source', region=BoxBounds(x=846, y=222, width=198, height=33), segment='7'),
    OcrField(name='Error (m)', region=BoxBounds(x=1139, y=221, width=117, height=34), segment='7'),

    OcrField(name='Species', region=BoxBounds(x=281, y=259, width=672, height=33), segment='7'),
    OcrField(name='GPS Waypoint', region=BoxBounds(x=1049, y=259, width=202, height=33), segment='7'),

    OcrField(name='Habitat', region=BoxBounds(x=242, y=295, width=1028, height=34), segment='7'),

    OcrField(name='Collection Date', region=BoxBounds(x=296, y=332, width=423, height=33), segment='7'),
    OcrField(name='Collector', region=BoxBounds(x=817, y=332, width=443, height=33), segment='7'),

    OcrField(name='Prep Date', region=BoxBounds(x=305, y=369, width=411, height=33), segment='7'),
    OcrField(name='Preparator', region=BoxBounds(x=830, y=369, width=428, height=33), segment='7'),

    # TODO: Collection Method

    # TODO: Preps

    # TODO: Tissue Date

    OcrField(name='Tissues', region=BoxBounds(x=839, y=488, width=218, height=40), segment='7'),
    OcrField(name='No. Tubes', region=BoxBounds(x=1163, y=489, width=81, height=39), segment='7'),

    # TODO: Tissue Preservation

    OcrField(name='Iris', region=BoxBounds(x=231, y=616, width=265, height=31), segment='7'),
    OcrField(name='Bill', region=BoxBounds(x=532, y=615, width=719, height=32), segment='7'),

    OcrField(name='Feet/Legs', region=BoxBounds(x=269, y=650, width=483, height=31), segment='7'),
    OcrField(name='Weight (g)', region=BoxBounds(x=817, y=650, width=163, height=31), segment='7'),
    OcrField(name='Age', region=BoxBounds(x=1030, y=650, width=103, height=31), segment='7'),
    OcrField(name='Sex', region=BoxBounds(x=1178, y=650, width=75, height=31), segment='7'),

    OcrField(name='Molt', region=BoxBounds(x=243, y=685, width=1017, height=30), segment='7'),

    OcrField(name='Gonads', region=BoxBounds(x=280, y=718, width=970, height=30), segment='7'),

    OcrField(name='Skull', region=BoxBounds(x=249, y=752, width=300, height=30), segment='7'),
    OcrField(name='Fat', region=BoxBounds(x=591, y=752, width=276, height=30), segment='7'),
    OcrField(name='Bursa', region=BoxBounds(x=932, y=752, width=330, height=30), segment='7'),

    OcrField(name='Stomach', region=BoxBounds(x=259, y=786, width=994, height=30), segment='7'),

    # TODO: Parasites

    OcrField(name='Remarks', region=BoxBounds(x=290, y=860, width=961, height=32), segment='7'),

    # TODO: Photos

    # TODO: Audio

    # TODO: Parasite Presence

    # TODO: See Back
]
