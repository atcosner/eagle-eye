import logging
import shutil
from pathlib import Path
from sqlalchemy.orm import Session

from src.database.copy import duplicate_field
from src.database.exporters.text_exporter import TextExporter
from src.database.fields.checkbox_field import CheckboxField
from src.database.fields.form_field import FormField
from src.database.fields.multi_checkbox_field import MultiCheckboxField
from src.database.fields.multi_checkbox_option import MultiCheckboxOption
from src.database.fields.text_field import TextField
from src.database.form_region import FormRegion
from src.database.reference_form import ReferenceForm
from src.database.validation.text_choice import TextChoice
from src.database.validation.text_validator import TextValidator
from src.util.paths import LocalPaths
from src.util.types import BoxBounds, FormLinkingMethod, FormAlignmentMethod
from src.util.validation import MultiCheckboxValidation, TextValidatorDatatype

logger = logging.getLogger(__name__)

FORM_BLANK_IMAGE_PATH = Path(__file__).parent / 'fn_field_form_v1.png'
assert FORM_BLANK_IMAGE_PATH.exists(), f'Form blank reference image does not exist: {FORM_BLANK_IMAGE_PATH}'
# SPECIES_LIST_PATH = Path(__file__).parent / 'ku_orn_taxonomy_reference.csv'
# assert SPECIES_LIST_PATH.exists(), f'Species list does not exist: {SPECIES_LIST_PATH}'


def add_fn_form_v1(session: Session) -> None:
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

    # add all fields to the singular region
    region = FormRegion(local_id=0, name='Form')
    region.fields = [
        FormField(
            text_field=TextField(
                name='Pseudo-Accession',
                visual_region=BoxBounds(x=333, y=46, width=220, height=56),
                text_validator=TextValidator(
                    text_regex=r'^[0-9]{4}-PA[0-9]{1,3}$',
                    error_tooltip='Pseudo-Accession must be in the format: <YYYY>-PA<NUMBER>',
                ),
            ),
        ),
    ]

    form.regions[region.local_id] = region
    session.add(form)
    session.commit()
