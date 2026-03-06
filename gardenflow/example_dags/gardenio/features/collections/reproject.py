"""
Example DAG: reproject a feature collection to a new SRID.

Demonstrates using the ReprojectCollectionOperator to transform
all geometries in a collection to a new coordinate reference
system, rebuild spatial indexes, and invalidate tile caches.
"""

from datetime import datetime, timedelta

from airflow.sdk import Param

from gardenflow.core.dags import GardenDAG
from gardenflow.operators.gardenio.features.collections import (
    ReprojectCollectionOperator,
)

default_args = {
    "owner": "gardenio",
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 0,
    "retry_delay": timedelta(minutes=1),
}

with GardenDAG(
    dag_id="reproject_collection",
    dag_display_name="Reproject Collection",
    default_args=default_args,
    description=(
        "Reproject a feature collection to a new coordinate "
        "reference system"
    ),
    schedule=None,
    start_date=datetime(2024, 1, 1),
    catchup=False,
    params={
        "collection": Param(
            type="string",
            description="Collection name",
            minLength=1,
            format="feature-collection",
        ),
        "srid": Param(
            type="integer",
            description="Target SRID (e.g. 3857, 4326)",
            minimum=1,
        ),
    },
) as dag:
    ReprojectCollectionOperator(
        task_id="reproject",
        collection="{{ params.collection }}",
        srid="{{ params.srid }}",
    )
