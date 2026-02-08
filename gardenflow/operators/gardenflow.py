from airflow.models import BaseOperator

from gardenflow.hooks.gardenflow import GardenflowHook


class GardenflowOperator(BaseOperator):
    """Operator for interacting with GardenIO services."""

    def __init__(
        self,
        gardenflow_conn_id: str = GardenflowHook.default_conn_name,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.gardenflow_conn_id = gardenflow_conn_id

    def execute(self, context):
        hook = GardenflowHook(
            gardenflow_conn_id=self.gardenflow_conn_id,
        )
        return hook
