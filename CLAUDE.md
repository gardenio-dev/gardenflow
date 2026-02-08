# CLAUDE.md

Project context for Claude Code.

## Project

Gardenflow is an Apache Airflow 3 provider package for GardenIO.
It is part of the GardenIO family of projects
(https://github.com/gardenio-dev).

## Versions

- Python version: defined in `.python-version` (currently 3.11.3)
- Airflow version: defined in `.airflow-version` (currently 3.1.7)
- These files are the single source of truth for their respective
  versions.

## Build & Run

- **Task runner**: `just` (justfiles at root and in `docker/dev/`)
- **Package manager**: `uv` (with `hatchling` build backend)
- **Python version management**: `pyenv` (inside dev container)
- **Setup**: `just setup` -- copies `.env.example` to `.env` if
  needed, creates `temp/` dir, creates Airflow DB, installs deps
- **Tests**: `just test` -- runs pytest, ruff check, ruff format
- **Docker build**: `cd docker/dev && just build`
- **Docker up**: `cd docker/dev && just up`

## Environment

- `.env.example` documents all environment variables and is
  committed to version control.
- `.env` is the local working copy, created by `just setup` from
  `.env.example` if it doesn't exist. It is git-ignored.
- `temp/` is a git-ignored directory for developer scratch data.

## Architecture

### Provider Package (`gardenflow/`)

Standard Airflow provider structure:
- `gardenflow/__init__.py` -- provider metadata, `get_provider_info()`
- `gardenflow/hooks/` -- hooks extending `BaseHook`
- `gardenflow/operators/` -- operators extending `BaseOperator`
- `gardenflow/sensors/` -- sensors extending `BaseSensorOperator`
- `gardenflow/example_dags/` -- example DAGs

Entry point registered in `pyproject.toml` under
`[project.entry-points.apache_airflow_provider]`.

### Dev Environment

- VS Code dev container (Ubuntu 24.04 base)
- Airflow runs **inside** the dev container (not as a sidecar)
- Airflow uses CeleryExecutor with Redis as broker
- PostGIS sidecar on host port 54321 for Airflow backend DB
- Redis sidecar on host port 6379

### Dev Stack Services

| Service | Container Name           | Host Port |
|---------|--------------------------|-----------|
| Dev     | gardenflow-dev-vscode    | --        |
| PostGIS | gardenflow-dev-postgis   | 54321     |
| Redis   | gardenflow-dev-redis     | 6379      |

PostGIS hostname inside the stack: `postgis`
Redis hostname inside the stack: `redis`

## Code Style

- Line length: 79 characters
- Linter/formatter: `ruff`
- Format on save enabled in VS Code
- Follow existing patterns in the codebase

## Testing

- Framework: `pytest`
- Test directory: `tests/` (mirrors `gardenflow/` structure)
- Run: `just test` or `uv run pytest tests/`
