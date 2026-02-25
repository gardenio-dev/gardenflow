"""
Example DAG: extract a .zip archive within the tenant's home directory.

Demonstrates using the ExtractFilesOperator to unpack a zip archive
from one location in the tenant's home directory to another.
"""

from datetime import datetime, timedelta

from airflow.sdk import Param

from gardenflow.core.dags import GardenDAG
from gardenflow.operators.gardenio.files import ExtractFilesOperator

default_args = {
    "owner": "gardenio",
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 0,
    "retry_delay": timedelta(minutes=1),
}

with GardenDAG(
    dag_id="extract_files",
    dag_display_name="Extract Files",
    default_args=default_args,
    description="Extract a .zip archive within the tenant's home directory",
    schedule=None,
    start_date=datetime(2024, 1, 1),
    catchup=False,
    params={
        "source": Param(
            type="string",
            description="Source archive path (relative to tenant home)",
            minLength=1,
            format="file-path",
        ),
        "dest": Param(
            default="",
            type="string",
            description=(
                "Destination directory (relative to tenant home). "
                "Defaults to the source path without the .zip extension."
            ),
            format="dir-path",
        ),
    },
) as dag:
    ExtractFilesOperator(
        task_id="extract",
        source="{{ params.source }}",
        dest="{{ params.dest }}",
    )
