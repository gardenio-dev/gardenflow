__version__ = "0.1.0"


def get_provider_info():
    return {
        "package-name": "gardenflow",
        "name": "Gardenflow",
        "description": "An Apache Airflow provider for GardenIO.",
        "connection-types": [
            {
                "connection-type": "gardenflow",
                "hook-class-name": (
                    "gardenflow.hooks.gardenflow.GardenflowHook"
                ),
            }
        ],
        "versions": [__version__],
    }
