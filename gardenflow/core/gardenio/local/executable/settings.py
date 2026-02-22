from pathlib import Path

from pydantic import ConfigDict, Field

from gardenflow.core.settings.base import BaseSettings, env_prefix


class GardenIOLocalExecutableSettings(BaseSettings):
    """Settings for the local executable version of GardenIO."""

    model_config = ConfigDict(
        env_prefix=env_prefix("gardenio", "local", "executable"),
        title="GardenIO Local Executable Settings",
    )

    executable: Path = Field(
        default=Path.cwd() / "bin" / "gardenio",
        description="The path to the gardenio executable.",
    )
