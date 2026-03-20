"""GardenIO feature collection operators."""

from gardenflow.core.logging import logger
from gardenflow.operators.gardenio.base import GardenioOperator


class ReprojectCollectionOperator(GardenioOperator):
    """Reproject a feature collection to a new SRID.

    Delegates to :meth:`GardenIOClient.reproject` and streams
    the command output to the Airflow task log.
    """

    template_fields = ("collection", "srid")

    def __init__(
        self,
        collection: str,
        srid: int,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.collection = collection
        self.srid = srid

    def execute(self, context):
        """Execute the reproject command."""
        client = self.get_client(context)
        log = logger()

        for line in client.reproject(
            collection=self.collection,
            srid=int(self.srid),
        ):
            log.info(line)
