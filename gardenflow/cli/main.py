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
    """Run the specified Airflow component using the Airflow CLI.

    :param component: The Airflow component to run. Must be one of 'api-
        server', 'standalone', 'scheduler', or 'dag-processor'.

    """
    load_dotenv(override=True)
    from airflow.__main__ import main

    args = ["airflow", component]
    sys.argv.clear()
    sys.argv.extend(args)
    sys.exit(main())


if __name__ == "__main__":
    """Runs the CLI entrypoint."""
    main()
