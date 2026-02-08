from airflow.sensors.base import BaseSensorOperator

from gardenflow.hooks.gardenflow import GardenflowHook


class GardenflowSensor(BaseSensorOperator):
    """Sensor for polling GardenIO services."""

    def __init__(
        self,
        gardenflow_conn_id: str = GardenflowHook.default_conn_name,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.gardenflow_conn_id = gardenflow_conn_id

    def poke(self, context):
        hook = GardenflowHook(
            gardenflow_conn_id=self.gardenflow_conn_id,
        )
        # TODO: Implement polling logic.
        return True
