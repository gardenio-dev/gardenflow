"""Base class for GardenIO operators."""

from airflow.models import BaseOperator

from gardenflow.core.gardenio.services import GardenIOClient


class GardenioOperator(BaseOperator):
    """Base operator for GardenIO tasks.

    Resolves the tenant from the ``gardenio`` DAG parameter
    injected by GardenIO at trigger time and provides a
    connected :class:`GardenIOClient` to subclasses.
    """

    def get_tenant(self, context) -> str:
        """Get the tenant ID from the GardenIO context parameter.

        :param context: Airflow task context
        :returns: the tenant identifier
        """
        return context["params"]["gardenio"]["tenant"]

    def get_client(self, context) -> GardenIOClient:
        """Get a GardenIO client for the current tenant.

        :param context: Airflow task context
        :returns: a connected GardenIOClient
        """
        return GardenIOClient.connect(tenant=self.get_tenant(context))
