from collections.abc import Generator

from gardenflow.core.gardenio.local.executable.executors import (
    StreamingExecutor,
)
from gardenflow.core.gardenio.local.executable.settings import (
    GardenIOLocalExecutableSettings,
)
from gardenflow.core.gardenio.services import GardenIOClient
from gardenflow.core.settings.base import configured


class LocalExecutableGardenIOClient(GardenIOClient):
    """GardenIO client that uses a local executable."""

    @configured()
    def __init__(
        self,
        tenant: str,
        settings: GardenIOLocalExecutableSettings,
    ):
        super().__init__(tenant=tenant)
        self._settings = settings

    def ogr2ogr_load(
        self,
        path: str,
        schema: str | None = None,
        layers: list[str] | None = None,
        fid_column: str | None = None,
        geom_column: str | None = None,
        nlt: str | None = None,
        a_srs: str | None = None,
        t_srs: str | None = None,
        s_srs: str | None = None,
        dim: str | None = None,
        launder: bool = False,
        overwrite: bool = False,
        update: bool = False,
        append: bool = False,
        upsert: bool = False,
        preserve_fid: bool = False,
        no_copy: bool = False,
        timeout: int | None = None,
        fitgeom: bool = False,
        bless: bool = False,
    ) -> Generator[str, None, None]:
        """Load data into PostGIS using ogr2ogr."""
        args = ["ogr2ogr", "load", path, self.tenant]

        if schema:
            args.extend(["--schema", schema])
        for layer in layers or []:
            args.extend(["--layer", layer])
        if fid_column:
            args.extend(["--fid-column", fid_column])
        if geom_column:
            args.extend(["--geom-column", geom_column])
        if nlt:
            args.extend(["--nlt", nlt])
        if a_srs:
            args.extend(["--a-srs", a_srs])
        if t_srs:
            args.extend(["--t-srs", t_srs])
        if s_srs:
            args.extend(["--s-srs", s_srs])
        if dim:
            args.extend(["--dim", dim])
        if launder:
            args.append("--launder")
        if overwrite:
            args.append("--overwrite")
        if update:
            args.append("--update")
        if append:
            args.append("--append")
        if upsert:
            args.append("--upsert")
        if preserve_fid:
            args.append("--preserve-fid")
        if no_copy:
            args.append("--no-copy")
        if timeout:
            args.extend(["--timeout", str(timeout)])
        if fitgeom:
            args.append("--fitgeom")
        if bless:
            args.append("--bless")

        executor = StreamingExecutor(
            self._settings.executable,
        )
        yield from executor.run(*args)
