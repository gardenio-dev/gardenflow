"""
Example DAG: load a geospatial file into PostGIS via ogr2ogr.

Demonstrates using the Ogr2OgrLoadOperator to import a file
from the tenant's home directory into a PostGIS schema.
"""

from datetime import datetime, timedelta

from airflow.sdk import Param

from gardenflow.core.dags import GardenDAG
from gardenflow.operators.gardenio.ogr2ogr import (
    Ogr2OgrLoadOperator,
)

default_args = {
    "owner": "gardenio",
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 0,
    "retry_delay": timedelta(minutes=1),
}

with GardenDAG(
    dag_id="load_ogr",
    dag_display_name="Load OGR Data",
    default_args=default_args,
    description="Load a geospatial data file into PostGIS",
    schedule=None,
    start_date=datetime(2024, 1, 1),
    catchup=False,
    params={
        "path": Param(
            type="string",
            description="Source file path (relative to tenant home)",
            minLength=1,
            format="file-path",
        ),
        "schema": Param(
            default="public",
            type="string",
            description="Target PostGIS schema",
        ),
        "layers": Param(
            default=[],
            type="array",
            description="Layer names to load",
        ),
        "fid_column": Param(
            default="",
            type="string",
            description="FID column name",
        ),
        "geom_column": Param(
            default="",
            type="string",
            description="Geometry column name",
        ),
        "nlt": Param(
            default="CONVERT_TO_LINEAR",
            type="string",
            description="Geometry type conversion",
        ),
        "a_srs": Param(
            default="",
            type="string",
            description="Assign output SRS (no reprojection)",
        ),
        "t_srs": Param(
            default="EPSG:4326",
            type="string",
            description="Target SRS (reprojects)",
        ),
        "s_srs": Param(
            default="",
            type="string",
            description="Override source SRS",
        ),
        "dim": Param(
            default="",
            type="string",
            description="Coordinate dimension (XY, XYZ, XYM, XYZM, layer_dim)",
        ),
        "launder": Param(
            default=False,
            type="boolean",
            description="Launder column names",
        ),
        "overwrite": Param(
            default=False,
            type="boolean",
            description="Overwrite existing tables",
        ),
        "update": Param(
            default=False,
            type="boolean",
            description="Open output datasource in update mode",
        ),
        "append": Param(
            default=False,
            type="boolean",
            description="Append to existing tables",
        ),
        "upsert": Param(
            default=False,
            type="boolean",
            description="Upsert features",
        ),
        "preserve_fid": Param(
            default=False,
            type="boolean",
            description="Preserve source feature IDs",
        ),
        "no_copy": Param(
            default=False,
            type="boolean",
            description="Disable PostgreSQL COPY mode",
        ),
        "timeout": Param(
            default=0,
            type="integer",
            description="Timeout in seconds (0 = no timeout)",
            minimum=0,
        ),
        "fitgeom": Param(
            default=False,
            type="boolean",
            description="Fit geometry type after loading",
        ),
        "bless": Param(
            default=True,
            type="boolean",
            description="Bless loaded tables as feature collections",
        ),
    },
) as dag:
    Ogr2OgrLoadOperator(
        task_id="load",
        path="{{ params.path }}",
        schema="{{ params.schema }}",
        layers="{{ params.layers }}",
        fid_column="{{ params.fid_column }}",
        geom_column="{{ params.geom_column }}",
        nlt="{{ params.nlt }}",
        a_srs="{{ params.a_srs }}",
        t_srs="{{ params.t_srs }}",
        s_srs="{{ params.s_srs }}",
        dim="{{ params.dim }}",
        launder="{{ params.launder }}",
        overwrite="{{ params.overwrite }}",
        update="{{ params.update }}",
        append="{{ params.append }}",
        upsert="{{ params.upsert }}",
        preserve_fid="{{ params.preserve_fid }}",
        no_copy="{{ params.no_copy }}",
        timeout="{{ params.timeout }}",
        fitgeom="{{ params.fitgeom }}",
        bless="{{ params.bless }}",
    )
