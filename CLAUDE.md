# CLAUDE.md

Project context for Claude Code.

## Project

Gardenflow is an Apache Airflow 3 provider package for GardenIO.
It is part of the GardenIO family of projects
(https://github.com/gardenio-dev).

### GardenIO Context

GardenIO (https://github.com/gardenio-dev/gardenio, `development`
branch) is a multi-tenant geospatial data management API built in
Rust/Axum. It implements several OGC API standards, including
**OGC API - Processes**, which is backed by Airflow via Gardenflow.

The integration is bidirectional:
- **GardenIO -> Airflow**: GardenIO's `AirflowProcessService`
  translates OGC Processes requests into Airflow REST API v2
  calls (trigger DAG runs, poll status, fetch results).
- **Airflow -> GardenIO**: DAGs use Gardenflow hooks/operators
  to call back into GardenIO's API.

Key conventions for the Airflow integration are documented
in the **Writing DAGs for GardenIO** section below and in
`README.md`.

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

Additional package directories:
- `gardenflow/core/` -- shared internals (e.g. structlog-based
  logging)
- `gardenflow/modules/` -- domain-specific logic organized by
  tool/library (e.g. `modules/gdal/` for ogr2ogr / ogrinfo
  wrappers)
- `gardenflow/core/cli/` -- CLI entrypoint
  (`gardenflow -c <component>`) that delegates to the Airflow CLI
  after loading `.env`

### Dev Environment

- VS Code dev container (Ubuntu 24.04 base)
- Container user: `vscode`
- Python is managed by `pyenv` (the `uv` package manager
  installs into the `pyenv`-managed interpreter)
- After changing `pyproject.toml` entry points or
  dependencies, re-run `just setup` to reinstall
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

## Git Workflow

- Default branch: `main`
- Long-lived integration branch: `development`
- Feature branches: `feature/<name>`

## Code Style

- Line length: 79 characters
- Linter/formatter: `ruff`
- Format on save enabled in VS Code
- Follow existing patterns in the codebase
- Prefer `@lru_cache()` functions over module-level constants.
  This keeps initialization lazy and makes it easy to swap in
  configuration-driven logic later without changing call sites.

## Testing

- Framework: `pytest`
- Test directory: `tests/` (mirrors `gardenflow/` structure)
- Run: `just test` or `uv run pytest tests/`

## Key Dependencies (beyond Airflow)

- `structlog` -- structured logging (`gardenflow/core/logging.py`)
- `click` -- CLI framework (`gardenflow/core/cli/main.py`)
- `python-dotenv` -- `.env` loading for the CLI
- `pandas` -- data manipulation
- `gdal-bin` -- installed in the dev container; GDAL CLI tools
  (`ogrinfo`, `ogr2ogr`) are available on `PATH`

## Writing DAGs for GardenIO

### Discovery

GardenIO discovers DAGs via the Airflow REST API filtered by
tag. A DAG appears as an OGC process only when it is:
1. **Tagged** with `gardenio` (or the configured tag)
2. **Active** (not archived)
3. **Not paused**

### Concept Mapping

| OGC API Processes | Airflow         |
|-------------------|-----------------|
| Process           | DAG             |
| Process ID        | `airflow.<dag_id>` |
| Process inputs    | DAG params      |
| Job               | DAG Run         |
| Job ID            | `airflow.<dag_id>:<dag_run_id>` |
| Execute           | Trigger DAG Run |

Status mapping: queued -> accepted, running -> running,
success -> successful, failed -> failed.

### DAG Template

```python
from airflow import DAG
from airflow.models.param import Param
from datetime import datetime

with DAG(
    dag_id="my_process",
    dag_display_name="My Process",
    description="What this process does",
    tags=["gardenio"],
    schedule=None,
    start_date=datetime(2024, 1, 1),
    catchup=False,
    params={
        "gardenio": Param(
            default={"tenant": "", "user": ""},
            type="object",
            description="GardenIO execution context "
                        "(injected automatically)",
        ),
        # User-facing params here using Param()
    },
) as dag:
    ...
```

### The `gardenio` Parameter

GardenIO injects `{"tenant": "...", "user": "..."}` into
every DAG run conf. Declare it in `params` so Airflow
validates the schema. GardenIO hides it from the OGC process
description -- API consumers never see it.

Access in tasks:
- Python: `context["params"]["gardenio"]["tenant"]`
- Jinja: `{{ params.gardenio.tenant }}`

### Defining Parameters with `Param`

Use `Param` for all user-facing parameters. The keyword
arguments map to JSON Schema and flow through to the OGC
process description. Always set `type`, `description`, and
`default`. Common keywords: `enum`, `minimum`, `maximum`,
`minLength`, `maxLength`, `pattern`.

Without `Param`, GardenIO infers the JSON Schema type from
the Python default value (str -> string, int -> integer,
etc.), but the result has no description, no default shown
to consumers, and no validation constraints. Prefer `Param`.

### Execution Model

GardenIO only supports async execution for Airflow DAGs:
1. Client POSTs to `.../execution` with inputs
2. GardenIO triggers a DAG run, returns `201` with job status
3. Client polls `.../jobs/{jobId}` for status
4. On completion, client fetches `.../jobs/{jobId}/results`

### Trigger Metadata

GardenIO sets `logical_date` (current UTC) and a `note`
(`Triggered via GardenIO by <user> (tenant: <tenant>)`) on
each DAG run for traceability in the Airflow UI.
