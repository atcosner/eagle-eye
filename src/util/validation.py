from enum import Enum


class MultiCheckboxValidation(Enum):
    NONE = 1
    REQUIRE_ONE = 2
    OPTIONAL = 3
