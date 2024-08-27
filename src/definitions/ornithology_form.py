from .util import TextField, BoxBounds, CheckboxMultiField, CheckboxOptionField


TOP_HALF_FIELDS = [
    # Header
    TextField(name='KT Number', region=BoxBounds(x=242, y=127, width=126, height=46)),
    TextField(name='Prep Number', region=BoxBounds(x=441, y=126, width=209, height=45)),
    TextField(name='KU Number', region=BoxBounds(x=708, y=125, width=201, height=46)),
    TextField(name='OT Number', region=BoxBounds(x=966, y=125, width=221, height=46)),

    # Body
    TextField(name='Locality', region=BoxBounds(x=277, y=187, width=783, height=32)),

    TextField(name='Latitude', region=BoxBounds(x=237, y=223, width=235, height=32)),
    TextField(name='Longitude', region=BoxBounds(x=534, y=221, width=235, height=34)),
    TextField(name='Source', region=BoxBounds(x=846, y=222, width=198, height=33)),
    TextField(name='Error (m)', region=BoxBounds(x=1139, y=221, width=117, height=34)),

    TextField(name='Species', region=BoxBounds(x=281, y=259, width=672, height=33)),
    TextField(name='GPS Waypoint', region=BoxBounds(x=1049, y=259, width=202, height=33)),

    TextField(name='Habitat', region=BoxBounds(x=242, y=295, width=1028, height=34)),

    TextField(name='Collection Date', region=BoxBounds(x=296, y=332, width=423, height=33)),
    TextField(name='Collector', region=BoxBounds(x=817, y=332, width=443, height=33)),

    TextField(name='Prep Date', region=BoxBounds(x=305, y=369, width=411, height=33)),
    TextField(name='Preparator', region=BoxBounds(x=830, y=369, width=428, height=33)),

    CheckboxMultiField(
        name='Collection Method',
        visual_region=BoxBounds(x=187, y=406, width=1056, height=49),
        options=[
            CheckboxOptionField(name='Shot', region=BoxBounds(x=337, y=427, width=11, height=11)),
            CheckboxOptionField(name='Net/Trap', region=BoxBounds(x=413, y=427, width=11, height=11)),
            CheckboxOptionField(name='Salvage', region=BoxBounds(x=535, y=427, width=11, height=11)),
            CheckboxOptionField(name='Unknown', region=BoxBounds(x=646, y=427, width=11, height=11)),
            CheckboxOptionField(
                name='Other',
                region=BoxBounds(x=723, y=427, width=11, height=11),
                text_region=BoxBounds(x=799, y=408, width=443, height=37),
            ),
        ],
    ),

    CheckboxMultiField(
        name='Preps',
        visual_region=BoxBounds(x=187, y=460, width=1055, height=48),
        options=[
            CheckboxOptionField(name='Round Skin', region=BoxBounds(x=269, y=469, width=11, height=11)),
            CheckboxOptionField(name='Skeleton', region=BoxBounds(x=406, y=469, width=11, height=11)),
            CheckboxOptionField(name='Partial Skeleton', region=BoxBounds(x=523, y=469, width=11, height=11)),
            CheckboxOptionField(name='Wingspread', region=BoxBounds(x=666, y=469, width=11, height=11)),
            CheckboxOptionField(name='Alcohol', region=BoxBounds(x=814, y=469, width=11, height=11)),
            CheckboxOptionField(
                name='Other',
                region=BoxBounds(x=884, y=469, width=11, height=11),
                text_region=BoxBounds(x=960, y=449, width=284, height=38),
            ),
        ],
    ),

    # TODO: Tissue Date

    TextField(name='Tissues', region=BoxBounds(x=839, y=488, width=218, height=40)),
    TextField(name='No. Tubes', region=BoxBounds(x=1163, y=489, width=81, height=39)),

    # TODO: Tissue Preservation

    TextField(name='Iris', region=BoxBounds(x=231, y=616, width=265, height=31)),
    TextField(name='Bill', region=BoxBounds(x=532, y=615, width=719, height=32)),

    TextField(name='Feet/Legs', region=BoxBounds(x=269, y=650, width=483, height=31)),
    TextField(name='Weight (g)', region=BoxBounds(x=817, y=650, width=163, height=31)),
    TextField(name='Age', region=BoxBounds(x=1030, y=650, width=103, height=31)),
    TextField(name='Sex', region=BoxBounds(x=1178, y=650, width=75, height=31)),

    TextField(name='Molt', region=BoxBounds(x=243, y=685, width=1017, height=30)),

    TextField(name='Gonads', region=BoxBounds(x=280, y=718, width=970, height=30)),

    TextField(name='Skull', region=BoxBounds(x=249, y=752, width=300, height=30)),
    TextField(name='Fat', region=BoxBounds(x=591, y=752, width=276, height=30)),
    TextField(name='Bursa', region=BoxBounds(x=932, y=752, width=330, height=30)),

    TextField(name='Stomach', region=BoxBounds(x=259, y=786, width=994, height=30)),

    # TODO: Parasites

    TextField(name='Remarks', region=BoxBounds(x=290, y=860, width=961, height=32)),

    # TODO: Photos

    # TODO: Audio

    # TODO: Parasite Presence

    # TODO: See Back
]
