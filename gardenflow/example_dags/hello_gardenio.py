"""
Sample GardenIO DAG for testing OGC API - Processes integration.

This DAG demonstrates a simple process that can be triggered via the
OGC API - Processes endpoint. It accepts a message input and outputs
a greeting.
"""

from datetime import datetime, timedelta

from airflow import DAG
from airflow.models.param import Param
from airflow.operators.python import PythonOperator


def greet(message: str = "World", **context) -> str:
    """Generate a greeting message."""
    greeting = f"Hello, {message}!"
    print(greeting)
    # Push to XCom for result retrieval
    context["ti"].xcom_push(key="greeting", value=greeting)
    return greeting


default_args = {
    "owner": "gardenio",
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=1),
}

with DAG(
    dag_id="hello_gardenio",
    default_args=default_args,
    description="A simple greeting process for GardenIO",
    schedule=None,  # Manual trigger only (schedule_interval renamed in v3)
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=["gardenio"],
    params={
        "message": Param(
            default="World",
            type="string",
            description="The message to include in the greeting",
        ),
    },
) as dag:
    greet_task = PythonOperator(
        task_id="greet",
        python_callable=greet,
        op_kwargs={
            "message": "{{ params.message }}",
        },
    )
