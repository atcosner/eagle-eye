from . import fn_form_v1
from . import kt_form_v8
from .types import ExampleForm

from src.util.types import FormLinkingMethod, FormAlignmentMethod


EXAMPLE_FORMS = [
    ExampleForm(
        name='KU Ornithology - KT Form v8',
        alignment_method=FormAlignmentMethod.ALIGNMENT_MARKS,
        link_method=FormLinkingMethod.PREVIOUS_REGION,
        regions=2,
        build_func=kt_form_v8.add_kt_form_v8,
    ),
    ExampleForm(
        name='KU Mammalogy - FN Form v1',
        alignment_method=FormAlignmentMethod.AUTOMATIC,
        link_method=FormLinkingMethod.PREVIOUS_IDENTIFIER,
        regions=6,
        build_func=fn_form_v1.add_fn_form_v1,
    ),
]
    