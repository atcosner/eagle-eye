from . import test_form_v1
from . import ornithology_form_v8
from .reference import ReferenceForm

from .. import FORMS_PATH

PRODUCTION_PATH = FORMS_PATH / 'production'
DEVELOPMENT_PATH = FORMS_PATH / 'dev'


SUPPORTED_FORMS = [
    ReferenceForm(
        name='Test Form v1',
        path=DEVELOPMENT_PATH / 'test_form_v1.png',
        reference_marks_count=8,
        regions=test_form_v1.ALL_REGIONS,
    ),
    ReferenceForm(
        name='Ornithology Field Form v8',
        path=PRODUCTION_PATH / 'kt_field_form_v8.png',
        reference_marks_count=16,
        regions=ornithology_form_v8.ALL_REGIONS,
        default=True,
    ),
]
