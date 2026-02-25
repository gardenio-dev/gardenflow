import zipfile
from collections.abc import Callable
from pathlib import Path

from gardenflow.core.files.local.settings import LocalFilesSettings
from gardenflow.core.files.services import FilesService
from gardenflow.core.settings.base import configured


class LocalFilesService(FilesService):
    """Files service backed by the local filesystem."""

    @configured()
    def __init__(self, tenant: str, settings: LocalFilesSettings):
        super().__init__(tenant=tenant)
        self._settings = settings

    def _tenant_home(self) -> Path:
        """Return the absolute path to the tenant's home directory."""
        return self._settings.home / self._tenant

    def _resolve(self, path: Path) -> Path:
        """Validate and resolve a relative path to an absolute one.

        :param path: a path relative to the tenant home directory
        :raises ValueError: if the path is absolute or contains ``..``
        :returns: the absolute filesystem path
        """
        if path.is_absolute():
            raise ValueError(
                f"Path must be relative to the tenant home: {path}"
            )
        if ".." in path.parts:
            raise ValueError(
                f"Path must not contain '..': {path}"
            )
        return self._tenant_home() / path

    def archive(
        self,
        source: Path,
        dest: Path,
        on_file_archived: Callable[[Path], None] | None = None,
    ) -> Path:
        """Create a .zip archive from a file or directory."""
        source_abs = self._resolve(source)
        dest_abs = self._resolve(dest)
        dest_abs.parent.mkdir(parents=True, exist_ok=True)

        with zipfile.ZipFile(
            dest_abs, "w", zipfile.ZIP_DEFLATED
        ) as zf:
            if source_abs.is_file():
                zf.write(source_abs, source_abs.name)
                if on_file_archived:
                    on_file_archived(source)
            else:
                for file in sorted(source_abs.rglob("*")):
                    if file.is_file():
                        arcname = file.relative_to(
                            source_abs.parent
                        )
                        zf.write(file, arcname)
                        if on_file_archived:
                            on_file_archived(
                                file.relative_to(self._tenant_home())
                            )

        return dest

    def extract(
        self,
        source: Path,
        dest: Path,
        on_file_extracted: Callable[[Path], None] | None = None,
    ) -> Path:
        """Extract a .zip archive."""
        source_abs = self._resolve(source)
        dest_abs = self._resolve(dest)
        dest_abs.mkdir(parents=True, exist_ok=True)

        with zipfile.ZipFile(source_abs, "r") as zf:
            for member in zf.namelist():
                zf.extract(member, dest_abs)
                if on_file_extracted:
                    on_file_extracted(dest / member)

        return dest
