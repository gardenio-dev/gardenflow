# Gardenflow

An Apache Airflow 3 provider for [GardenIO](https://github.com/gardenio-dev/gardenio).

## Overview

Gardenflow provides custom hooks, operators, and sensors for
integrating Apache Airflow with GardenIO services.

## Requirements

- Python 3.11+
- Apache Airflow 3.0+

## Development

This project uses a VS Code dev container for development.

### Prerequisites

- [Docker](https://www.docker.com/)
- [VS Code](https://code.visualstudio.com/) with the
  [Dev Containers](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)
  extension

### Getting Started

1. Clone the repository.
2. Open the project in VS Code.
3. When prompted, select **Reopen in Container** (or run the
   `Dev Containers: Reopen in Container` command).
4. The `just setup` command runs automatically on container start,
   which:
   - Copies `.env.example` to `.env` (if `.env` doesn't exist)
   - Creates the `temp/` directory for scratch data
   - Creates the Airflow database in PostGIS
   - Installs project dependencies via `uv`

### Environment Variables

Environment variables are documented in `.env.example`. To configure:

```bash
cp .env.example .env
```

Edit `.env` as needed. This file is excluded from version control.

### Building the Dev Image

From `docker/dev`:

```bash
just build
```

### Running Tests

```bash
just test
```

This runs pytest, ruff lint checks, and ruff format checks.

## Project Structure

```
gardenflow/
├── .env.example        # Environment variable documentation
├── gardenflow/
│   ├── hooks/          # Airflow hooks
│   ├── operators/      # Airflow operators
│   ├── sensors/        # Airflow sensors
│   └── example_dags/   # Example DAGs
├── tests/              # Tests (mirrors gardenflow/ structure)
├── temp/               # Local scratch data (git-ignored)
├── docker/dev/         # Dev container image definition
└── .devcontainer/      # VS Code dev container config
```

## Dev Stack

| Service  | Host Port | Description                        |
|----------|-----------|------------------------------------|
| PostGIS  | 54321     | PostgreSQL + PostGIS (Airflow DB)  |
| Redis    | 6379      | Celery broker                      |
| Airflow  | 8080      | Airflow UI (runs inside dev container) |

## Tools

- **just** -- task runner
- **uv** -- Python package manager
- **pyenv** -- Python version manager (in dev container)
- **ruff** -- linter and formatter

## License

Apache License 2.0
