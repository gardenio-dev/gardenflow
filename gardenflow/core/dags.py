"""DAG utilities for GardenIO integration."""

from functools import lru_cache

from airflow import DAG
from airflow.models.param import Param


@lru_cache()
def gardenio_tag() -> str:
    """Get the GardenIO tag."""
    return "gardenio"


@lru_cache()
def gardenio_param() -> Param:
    """Get the GardenIO Param."""
    return Param(
        default={"tenant": "", "user": ""},
        type="object",
        description=("GardenIO execution context (injected automatically)"),
    )


def GardenDAG(*args, **kwargs) -> DAG:
    """Create a DAG pre-configured for GardenIO.

    Ensures the ``gardenio`` tag is present and the
    ``gardenio`` Param is declared, then delegates to
    :class:`airflow.DAG`.

    Usage::

        from gardenflow.core.dags import GardenDAG

        with GardenDAG(
            dag_id="my_process",
            schedule=None,
            start_date=datetime(2024, 1, 1),
            catchup=False,
            params={...},
        ) as dag:
            ...
    """
    tags = list(kwargs.get("tags") or [])
    if gardenio_tag() not in tags:
        tags.append(gardenio_tag())
    kwargs["tags"] = tags

    params = dict(kwargs.get("params") or {})
    if gardenio_tag() not in params:
        params[gardenio_tag()] = gardenio_param()
    kwargs["params"] = params

    kwargs.setdefault("render_template_as_native_obj", True)

    return DAG(*args, **kwargs)
