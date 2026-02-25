"""GardenIO files operators."""

from pathlib import Path

from gardenflow.core.files.services import FilesService
from gardenflow.core.logging import logger
from gardenflow.operators.gardenio.base import GardenioOperator


class ExtractFilesOperator(GardenioOperator):
    """Extract a .zip archive within the tenant's home directory.

    Delegates to :meth:`FilesService.extract` and logs each
    extracted file path to the Airflow task log.

    Returns the destination directory path (relative to the
    tenant home) as a string, available to downstream tasks
    via XCom.
    """

    template_fields = ("source", "dest")

    def __init__(
        self,
        source: str,
        dest: str = "",
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.source = source
        self.dest = dest

    def execute(self, context):
        """Execute the file extraction."""
        files = FilesService.connect(
            tenant=self.get_tenant(context)
        )
        log = logger()

        source = Path(self.source)
        dest = Path(self.dest) if self.dest else source.with_suffix("")

        log.info(
            "Extracting archive",
            source=str(source),
            dest=str(dest),
        )

        result = files.extract(
            source=source,
            dest=dest,
            on_file_extracted=lambda p: log.info(
                "Extracted", path=str(p)
            ),
        )

        return str(result)
