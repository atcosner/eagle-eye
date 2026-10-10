from typing import NamedTuple, Callable

from src.util.types import FormLinkingMethod, FormAlignmentMethod


class ExampleForm(NamedTuple):
    name: str
    alignment_method: FormAlignmentMethod
    link_method: FormLinkingMethod
    regions: int
    build_func: Callable
