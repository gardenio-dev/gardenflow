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

## Writing DAGs for GardenIO

### How GardenIO Discovers Your DAGs

GardenIO calls the Airflow REST API (`/api/v2/dags`) and
filters by **tag**. Only DAGs that meet all three conditions
appear as processes:

1. **Tagged** with a configured tag (default: `gardenio`)
2. **Active** (not archived)
3. **Not paused**

If your DAG is missing or not showing up, check these three
things first.

### Concept Mapping

| OGC API Processes | Airflow         |
|-------------------|-----------------|
| Process           | DAG             |
| Process ID        | DAG ID          |
| Process inputs    | DAG params      |
| Job               | DAG Run         |
| Job ID            | DAG Run ID      |
| Execute           | Trigger DAG Run |
| Job status        | DAG Run state   |

#### Process IDs

GardenIO qualifies process IDs with the service name:

```
airflow.<dag_id>
```

For example, a DAG with `dag_id="etl_buildings"` becomes
process `airflow.etl_buildings` in the API.

#### Job IDs

Job IDs combine the process ID and the Airflow run ID:

```
airflow.<dag_id>:<dag_run_id>
```

#### Job Status Mapping

| Airflow State | OGC Job Status |
|---------------|----------------|
| `queued`      | `accepted`     |
| `running`     | `running`      |
| `success`     | `successful`   |
| `failed`      | `failed`       |

### DAG Requirements

#### Minimal DAG

The simplest DAG that GardenIO can discover:

```python
from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime

with DAG(
    dag_id="hello_gardenio",
    dag_display_name="Hello GardenIO",
    description="A minimal GardenIO-compatible DAG",
    tags=["gardenio"],
    schedule=None,           # On-demand only
    start_date=datetime(2024, 1, 1),
    catchup=False,
    params={},
) as dag:
    BashOperator(
        task_id="greet",
        bash_command='echo "Hello from GardenIO"',
    )
```

Key points:
- `tags` must include `"gardenio"` (or whatever tag your
  GardenIO instance is configured to filter on).
- `schedule=None` is typical for on-demand processes.
- `catchup=False` prevents backfill runs.

#### The `gardenio` Parameter

When GardenIO triggers your DAG, it injects a `gardenio`
object into the run configuration (`conf`). This tells your
DAG which tenant and user initiated the execution.

**Structure:**

```json
{
  "gardenio": {
    "tenant": "my-tenant",
    "user": "alice@example.com"
  }
}
```

| Field    | Type             | Description                     |
|----------|------------------|---------------------------------|
| `tenant` | `string`         | Tenant that triggered the run   |
| `user`   | `string \| null` | Authenticated user, if any      |

**Declare it in your DAG's `params`** so Airflow validates
the schema and provides a default for manual triggers:

```python
from airflow.models.param import Param

with DAG(
    dag_id="my_process",
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
    },
) as dag:
    ...
```

GardenIO **hides** the `gardenio` parameter from the OGC
process description. API consumers never see it as an input
and cannot override it -- GardenIO always injects the real
values.

**Accessing the context in tasks:**

```python
# In a PythonOperator
def my_task(**context):
    gardenio = context["params"]["gardenio"]
    tenant = gardenio["tenant"]
    user = gardenio.get("user")
    print(f"Running for tenant: {tenant}, user: {user}")

# In a template (Jinja)
BashOperator(
    task_id="show_tenant",
    bash_command='echo "Tenant: {{ params.gardenio.tenant }}"',
)
```

#### Defining Parameters with `Param`

Use Airflow's `Param` class to define your DAG parameters.
`Param` produces a JSON Schema that GardenIO passes through
to the OGC process description, giving API consumers rich
type information, descriptions, defaults, and validation
constraints.

```python
from airflow.models.param import Param

params={
    "message": Param(
        default="World",
        type="string",
        description="The greeting message",
    ),
    "count": Param(
        default=1,
        type="integer",
        description="How many times to repeat",
        minimum=1,
        maximum=100,
    ),
    "format": Param(
        default="json",
        type="string",
        description="Output format",
        enum=["json", "csv", "geojson"],
    ),
    "overwrite": Param(
        default=False,
        type="boolean",
        description="Replace existing data",
    ),
}
```

The `Param` keyword arguments map directly to JSON Schema
keywords. Common ones:

| Keyword       | Applies to          | Example              |
|---------------|---------------------|----------------------|
| `type`        | all                 | `"string"`           |
| `description` | all                 | `"The input file"`   |
| `default`     | all                 | `42`                 |
| `enum`        | string, integer     | `["a", "b", "c"]`   |
| `minimum`     | integer, number     | `0`                  |
| `maximum`     | integer, number     | `100`                |
| `minLength`   | string              | `1`                  |
| `maxLength`   | string              | `255`                |
| `pattern`     | string              | `"^[a-z]+$"`         |

GardenIO passes the full JSON Schema through, so any
standard JSON Schema keyword you add to `Param` will be
visible to API consumers in the process description.

**Example process description output (abbreviated):**

```json
{
  "id": "airflow.import_shapefile",
  "inputs": {
    "message": {
      "description": "The greeting message",
      "schema": {
        "type": "string",
        "description": "The greeting message",
        "default": "World"
      }
    },
    "count": {
      "description": "How many times to repeat",
      "schema": {
        "type": "integer",
        "description": "How many times to repeat",
        "default": 1,
        "minimum": 1,
        "maximum": 100
      }
    }
  }
}
```

#### Plain Default Fallback

If you don't use `Param`, GardenIO falls back to inferring
the JSON Schema type from the parameter's default value.
This works but produces minimal schemas with no description,
no default, and no validation constraints.

| Python Default Type | Inferred Schema Type |
|---------------------|----------------------|
| `str`               | `string`             |
| `int`               | `integer`            |
| `float`             | `number`             |
| `bool`              | `boolean`            |
| `list`              | `array`              |
| `dict`              | `object`             |
| `None`              | *(no type)*          |

**Example (works but not recommended):**

```python
# Plain defaults -- API consumers see types but no
# descriptions, defaults, or constraints.
params={
    "source_url": "https://example.com/data.shp",
    "srid": 4326,
    "overwrite": False,
}
```

Prefer `Param` whenever possible.

#### Putting It Together

A complete params block using `Param` for user inputs and
the `gardenio` context:

```python
from airflow.models.param import Param

params={
    "gardenio": Param(
        default={"tenant": "", "user": ""},
        type="object",
        description="GardenIO execution context "
                    "(injected automatically)",
    ),
    "source_url": Param(
        default="",
        type="string",
        description="URL of the shapefile to import",
    ),
    "target_collection": Param(
        default="",
        type="string",
        description="Target collection name",
    ),
    "srid": Param(
        default=4326,
        type="integer",
        description="Source coordinate reference system",
    ),
    "overwrite": Param(
        default=False,
        type="boolean",
        description="Replace existing data if present",
    ),
}
```

API consumers execute the process by sending:

```
POST /api/my-tenant/processes/airflow.import_shapefile/execution
Content-Type: application/json
```

```json
{
  "inputs": {
    "source_url": "https://data.gov/parcels.shp",
    "target_collection": "parcels",
    "srid": 4326,
    "overwrite": true
  }
}
```

GardenIO merges user inputs with the injected `gardenio`
context and sends the combined object as the DAG run's
`conf`:

```json
{
  "gardenio": {
    "tenant": "my-tenant",
    "user": "alice@example.com"
  },
  "source_url": "https://data.gov/parcels.shp",
  "target_collection": "parcels",
  "srid": 4326,
  "overwrite": true
}
```

All parameters are treated as optional (`minOccurs: 0`).

### Complete Example

A DAG that uses the GardenIO context to connect back to
the tenant's database:

```python
from airflow import DAG
from airflow.models.param import Param
from airflow.operators.python import PythonOperator
from datetime import datetime


def process_data(**context):
    gardenio = context["params"]["gardenio"]
    tenant = gardenio["tenant"]
    user = gardenio.get("user", "unknown")
    collection = context["params"]["target_collection"]

    # Use the tenant name to connect to the right database.
    # GardenIO convention: tenant name = database name.
    conn_str = (
        f"postgresql://postgres:postgres"
        f"@gardenio-dev-postgis:5432/{tenant}"
    )

    print(f"Processing for tenant={tenant} user={user}")
    print(f"Target collection: {collection}")
    print(f"Connection: {conn_str}")

    # ... your ETL logic here ...


with DAG(
    dag_id="etl_pipeline",
    dag_display_name="ETL Pipeline",
    description="Run an ETL pipeline for a tenant",
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
        "target_collection": Param(
            default="default_collection",
            type="string",
            description="Target collection name",
        ),
    },
) as dag:
    PythonOperator(
        task_id="process",
        python_callable=process_data,
    )
```

### Trigger Metadata

When GardenIO triggers a DAG run, it also sets:

- **`logical_date`** -- Current UTC timestamp.
- **`note`** -- A human-readable message:
  `Triggered via GardenIO by alice@example.com (tenant: my-tenant)`

The note appears in the Airflow UI on the DAG run detail
page, making it easy to trace who initiated a run.

### Execution Model

GardenIO only supports **asynchronous** execution for
Airflow DAGs. The flow is:

1. Client sends `POST .../execution` with inputs.
2. GardenIO triggers a DAG run and returns `201 Created`
   with the job status and a `Location` header.
3. Client polls `GET .../jobs/{jobId}` for status updates.
4. When the DAG run completes, client fetches results at
   `GET .../jobs/{jobId}/results`.
5. Client can cancel with `DELETE .../jobs/{jobId}`.

### GardenIO Configuration

GardenIO's Airflow connection is configured via environment
variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `GARDENIO__PROCESSES__AIRFLOW__BASE_URL` | *(required)* | Airflow API URL (e.g., `http://airflow:8080`) |
| `GARDENIO__PROCESSES__AIRFLOW__USERNAME` | `admin` | Auth username |
| `GARDENIO__PROCESSES__AIRFLOW__PASSWORD` | `airflow` | Auth password |
| `GARDENIO__PROCESSES__AIRFLOW__DAG_TAGS` | `gardenio` | Comma-separated tags to filter |
| `GARDENIO__PROCESSES__AIRFLOW__CACHE_TTL_PROCESSES` | `30` | Process list cache TTL (seconds) |
| `GARDENIO__PROCESSES__AIRFLOW__CACHE_TTL_JOBS` | `10` | Job status cache TTL (seconds) |
| `GARDENIO__PROCESSES__AIRFLOW__SERVICE_NAME` | `default` | Service instance name |

#### Multiple Tags

If you use multiple tags, separate them with commas:

```
GARDENIO__PROCESSES__AIRFLOW__DAG_TAGS=gardenio,etl,data-pipeline
```

A DAG only needs **one** matching tag to be discovered.

### DAG Checklist

When writing a new DAG for GardenIO:

- [ ] Set `tags` to include `"gardenio"` (or your
      configured tag)
- [ ] Set `schedule=None` and `catchup=False` for
      on-demand processes
- [ ] Declare a `gardenio` param (with `Param(type="object")`)
- [ ] Use `Param` for user-facing parameters with `type`,
      `description`, and `default`
- [ ] Access `params.gardenio.tenant` in tasks to identify
      the calling tenant
- [ ] Unpause the DAG so GardenIO can discover it

## License

Apache License 2.0
