from abc import ABC, abstractmethod
from collections.abc import Callable
from functools import lru_cache
from pathlib import Path
from typing import Self

from gardenflow.core.files.settings import FilesClientKind, FilesSettings
from gardenflow.core.settings.base import configured
from gardenflow.core.tenants.services import TenantService


class FilesService(TenantService, ABC):
    """Abstract base class for tenant-aware file services."""

    @abstractmethod
    def archive(
        self,
        source: Path,
        dest: Path,
        on_file_archived: Callable[[Path], None] | None = None,
    ) -> Path:
        """Create a .zip archive from a file or directory.

        All paths are relative to the tenant home directory.
        Absolute paths are not accepted.

        :param source: source file or directory to archive
        :param dest: destination archive path (e.g. ``backups/data.zip``)
        :param on_file_archived: optional callback invoked with the
            relative path of each file as it is added to the archive
        :returns: relative path to the created archive
        """

    @abstractmethod
    def extract(
        self,
        source: Path,
        dest: Path,
        on_file_extracted: Callable[[Path], None] | None = None,
    ) -> Path:
        """Extract a .zip archive.

        All paths are relative to the tenant home directory.
        Absolute paths are not accepted.

        :param source: archive file to extract
        :param dest: destination directory for extracted files
        :param on_file_extracted: optional callback invoked with the
            relative path of each file as it is extracted
        :returns: relative path to the extraction directory
        """

    @classmethod
    @lru_cache()
    @configured()
    def connect(cls, tenant: str, settings: FilesSettings) -> Self:
        """Connect to the files service for a given tenant."""
        if settings.kind == FilesClientKind.LOCAL:
            from gardenflow.core.files.local.services import (
                LocalFilesService,
            )

            return LocalFilesService(tenant=tenant)
        raise ValueError(
            f"Unsupported files client kind: {settings.kind}"
        )
