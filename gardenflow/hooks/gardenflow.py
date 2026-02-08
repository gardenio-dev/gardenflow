from airflow.hooks.base import BaseHook


class GardenflowHook(BaseHook):
    """Hook for interacting with GardenIO services."""

    conn_name_attr = "gardenflow_conn_id"
    default_conn_name = "gardenflow_default"
    conn_type = "gardenflow"
    hook_name = "Gardenflow"

    def __init__(
        self,
        gardenflow_conn_id: str = default_conn_name,
        *args,
        **kwargs,
    ):
        super().__init__()
        self.gardenflow_conn_id = gardenflow_conn_id
        self.connection = self.get_connection(self.gardenflow_conn_id)
