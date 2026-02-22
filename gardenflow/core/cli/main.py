import sys

import click
from dotenv import load_dotenv


@click.command()
@click.option(
    "-c",
    "--component",
    required=True,
    type=click.Choice(
        [
            "api-server",
            "standalone",
            "scheduler",
            "dag-processor",
            "triggerer",
            "celery worker",
        ]
    ),
)
def main(component: str):
    """Run an Airflow component."""
    load_dotenv(override=True)
    from airflow.__main__ import main

    args = ["airflow"] + component.split(" ")
    sys.argv.clear()
    sys.argv.extend(args)
    sys.exit(main())


if __name__ == "__main__":
    """Runs the CLI entrypoint."""
    main()
