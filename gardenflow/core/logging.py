import inspect
from functools import lru_cache, wraps
from typing import Any

import structlog


@lru_cache()
def logger() -> Any:
    """Get the module logger."""
    return structlog.get_logger(__name__.split(".")[0])


def traceable(
    tracer: str = "tracer",
):
    """
    Inject tracers.

    :param tracer: the name of the argument that holds the tracer
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
            tracer_ = params[tracer]
            if not issubclass(tracer_, str):
                raise TypeError(
                    f"{tracer_.__module__}.{tracer_.__class__.__name__} "
                    "is not a subclass of str."
                )
        except KeyError:
            settings_ = None

        @wraps(func)
        def wrapper(*args, **kwargs):
            """Call the function."""
            if tracer and not kwargs.get(tracer):
                kwargs[tracer] = settings_.get()
            return func(*args, **kwargs)

        return wrapper

    return decorator
