from abc import ABC, abstractmethod
from collections.abc import Generator
from functools import lru_cache
from typing import Self

from gardenflow.core.gardenio.settings import (
    GardenIOClientKind,
    GardenIOSettings,
)
from gardenflow.core.settings.base import configured
from gardenflow.core.tenants.services import TenantService


class GardenIOClient(TenantService, ABC):
    """Abstract base class for GardenIO clients."""

    @abstractmethod
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
        """Load data into PostGIS using ogr2ogr.

        :param path: source file path (relative to tenant
            home)
        :param schema: target schema
        :param layers: layer names to load
        :param fid_column: FID column name
        :param geom_column: geometry column name
        :param nlt: geometry type conversion
        :param a_srs: assign output SRS (no reprojection)
        :param t_srs: target SRS (reprojects)
        :param s_srs: override source SRS
        :param dim: coordinate dimension
        :param launder: launder column names
        :param overwrite: overwrite existing tables
        :param update: open output in update mode
        :param append: append to existing tables
        :param upsert: upsert features
        :param preserve_fid: preserve source feature IDs
        :param no_copy: disable PostgreSQL COPY mode
        :param timeout: timeout in seconds
        :param fitgeom: fit geometry type after loading
        :param bless: bless loaded tables as feature
            collections
        :yields: lines from the command output
        """

    @classmethod
    @lru_cache()
    @configured()
    def connect(cls, tenant: str, settings: GardenIOSettings) -> Self:
        """Connect to the GardenIO service for a given tenant."""

        if settings.kind == GardenIOClientKind.LOCAL_EXECUTABLE:
            from gardenflow.core.gardenio.local.executable.services import (
                LocalExecutableGardenIOClient,
            )

            return LocalExecutableGardenIOClient(tenant=tenant)
        raise ValueError(
            f"Unsupported GardenIO client kind: {settings.client_kind}"
        )
