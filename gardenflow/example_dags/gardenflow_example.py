from datetime import datetime

from airflow import DAG
from gardenflow.operators.gardenflow import GardenflowOperator

with DAG(
    dag_id="gardenflow_example",
    start_date=datetime(2025, 1, 1),
    schedule=None,
    catchup=False,
    tags=["gardenflow", "example"],
) as dag:
    gardenflow_task = GardenflowOperator(
        task_id="gardenflow_task",
        gardenflow_conn_id="gardenflow_default",
    )
