from enum import Enum

from pydantic import ConfigDict, Field

from gardenflow.core.settings.base import BaseSettings, env_prefix


class FilesClientKind(str, Enum):
    """Enum for files service client types."""

    LOCAL = "local"


class FilesSettings(BaseSettings):
    """Settings for the files service."""

    model_config = ConfigDict(
        env_prefix=env_prefix("files"),
        title="Files Settings",
    )

    kind: FilesClientKind = Field(
        default=FilesClientKind.LOCAL,
        description="The files service client type.",
    )
