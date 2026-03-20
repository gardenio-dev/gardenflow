from pathlib import Path

from pydantic import ConfigDict, Field

from gardenflow.core.settings.base import BaseSettings, env_prefix


class LocalFilesSettings(BaseSettings):
    """Settings for the local filesystem files service."""

    model_config = ConfigDict(
        env_prefix=env_prefix("files", "local"),
        title="Local Files Settings",
    )

    home: Path = Field(
        default=Path.cwd() / "temp" / "home",
        description="Root directory under which tenant home "
        "directories are resolved.",
    )
