from functools import lru_cache
from typing import Callable
from typing import Mapping

import pydantic
from pydantic import ConfigDict


@lru_cache(maxsize=2048)
def alias(field: str) -> str:
    """
    Generate an alias for a field name.

    :param field: the field name
    :returns: the alias
    """
    a = "".join(word.capitalize() for word in field.split("_"))
    return f"{a[0].lower()}{''.join(a[1:])}"


@lru_cache()
def json_encoders() -> Mapping[str, Callable]:
    return {
        # Add custom JSON encoders here.
        set: lambda s: tuple(s),
    }


class BaseModel(pydantic.BaseModel):
    """Base model for all models."""

    model_config = ConfigDict(
        alias_generator=alias,
        json_encoders=json_encoders(),
        frozen=False,
        populate_by_name=True,
        str_strip_whitespace=True,
        use_enum_values=True,
    )
