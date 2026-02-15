import inspect
from functools import lru_cache, wraps
from typing import Self

import pydantic_settings
from pydantic_settings import SettingsConfigDict


@lru_cache(maxsize=256)
def env_prefix(*pre: str, sep: str = "__") -> str:
    package = __package__.split(".")[0]
    return f"{sep.join((package.lower(), *pre))}{sep}"


class BaseSettings(pydantic_settings.BaseSettings):
    """Base class for settings."""

    model_config = SettingsConfigDict(frozen=True)

    @classmethod
    @lru_cache()
    def get(cls) -> Self:
        """Get the current settings."""
        return cls()


def configured(
    settings: str = "settings",
):
    """
    Inject settings.

    :param settings: the name of the argument that hold settings
    :return: the function wrapper
    """

    def decorator(func):
        """Create the function wrapper."""
        # Enumerate the function parameters.
        params = {
            p.name: p.annotation
            for p in inspect.signature(func).parameters.values()
        }
        try:
            settings_ = params[settings]
            if not issubclass(settings_, BaseSettings):
                raise TypeError(
                    f"{settings_.__module__}.{settings_.__class__.__name__} "
                    "is not a subclass of "
                    f"{BaseSettings.__module__}."
                    f"{BaseSettings.__class__.__name__}."
                )
        except KeyError:
            settings_ = None

        @wraps(func)
        def wrapper(*args, **kwargs):
            """Call the function."""
            if settings_ and not kwargs.get(settings):
                kwargs[settings] = settings_.get()
            return func(*args, **kwargs)

        return wrapper

    return decorator
