from dataclasses import dataclass
from pathlib import Path

from . import ornithology_form_v8
from . import test_form_v1
from .base_fields import BaseField


# TODO: Is there a better way to get this path?
FORMS_DIRECTORY = Path(__file__).parent.parent.parent / 'forms'
PRODUCTION_PATH = FORMS_DIRECTORY / 'production'
DEVELOPMENT_PATH = FORMS_DIRECTORY / 'dev'


@dataclass(frozen=True)
class ReferenceForm:
    name: str
    path: Path
    reference_marks_count: int
    regions: dict[str, list[BaseField]]

    def __post_init__(self):
        assert self.path.exists(), f'Form path does not exist: {self.path}'


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
    ),
]
