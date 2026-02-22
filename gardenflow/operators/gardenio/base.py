"""Base class for GardenIO operators."""

from airflow.models import BaseOperator

from gardenflow.core.gardenio.services import GardenIOClient


class GardenioOperator(BaseOperator):
    """Base operator for GardenIO tasks.

    Resolves the tenant from the ``gardenio`` DAG parameter
    injected by GardenIO at trigger time and provides a
    connected :class:`GardenIOClient` to subclasses.
    """

    def get_client(self, context) -> GardenIOClient:
        """Get a GardenIO client for the current tenant.

        :param context: Airflow task context
        :returns: a connected GardenIOClient
        """
        tenant = context["params"]["gardenio"]["tenant"]
        return GardenIOClient.connect(tenant=tenant)
