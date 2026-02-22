from enum import Enum

from pydantic import Field

from gardenflow.core.settings.base import BaseSettings


class GardenIOClientKind(str, Enum):
    """Enum for GardenIO client types."""

    LOCAL_EXECUTABLE = "local_executable"


class GardenIOSettings(BaseSettings):
    """Settings for GardenIO."""

    kind: GardenIOClientKind = Field(
        default=GardenIOClientKind.LOCAL_EXECUTABLE,
        description="The GardenIO client type.",
    )
