"""GardenIO ogr2ogr operators."""

from gardenflow.core.logging import logger
from gardenflow.operators.gardenio.base import GardenioOperator


class Ogr2OgrLoadOperator(GardenioOperator):
    """Load a geospatial data file into PostGIS via ogr2ogr.

    Delegates to :meth:`GardenIOClient.ogr2ogr_load` and
    streams the command output to the Airflow task log.
    """

    template_fields = (
        "path",
        "schema",
        "layers",
        "fid_column",
        "geom_column",
        "nlt",
        "a_srs",
        "t_srs",
        "s_srs",
        "dim",
        "launder",
        "overwrite",
        "update",
        "append",
        "upsert",
        "preserve_fid",
        "no_copy",
        "timeout",
        "fitgeom",
        "bless",
    )

    def __init__(
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
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.path = path
        self.schema = schema
        self.layers = layers
        self.fid_column = fid_column
        self.geom_column = geom_column
        self.nlt = nlt
        self.a_srs = a_srs
        self.t_srs = t_srs
        self.s_srs = s_srs
        self.dim = dim
        self.launder = launder
        self.overwrite = overwrite
        self.update = update
        self.append = append
        self.upsert = upsert
        self.preserve_fid = preserve_fid
        self.no_copy = no_copy
        self.timeout = timeout
        self.fitgeom = fitgeom
        self.bless = bless

    def execute(self, context):
        """Execute the ogr2ogr load command."""
        client = self.get_client(context)
        log = logger()

        for line in client.ogr2ogr_load(
            path=self.path,
            schema=self.schema,
            layers=self.layers,
            fid_column=self.fid_column,
            geom_column=self.geom_column,
            nlt=self.nlt,
            a_srs=self.a_srs,
            t_srs=self.t_srs,
            s_srs=self.s_srs,
            dim=self.dim,
            launder=self.launder,
            overwrite=self.overwrite,
            update=self.update,
            append=self.append,
            upsert=self.upsert,
            preserve_fid=self.preserve_fid,
            no_copy=self.no_copy,
            timeout=self.timeout,
            fitgeom=self.fitgeom,
            bless=self.bless,
        ):
            log.info(line)
