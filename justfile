set shell := ["bash", "-uc"]
set dotenv-load

# Ensure required databases exist.
ensure-databases:
    #!/usr/bin/env bash
    set -e
    echo "Ensuring required databases exist..."
    until PGPASSWORD=postgres pg_isready \
        -h postgis -U postgres \
        > /dev/null 2>&1; do
        echo "Waiting for PostgreSQL to be ready..."
        sleep 1
    done
    echo "PostgreSQL is ready. Checking databases..."
    if PGPASSWORD=postgres psql \
        -h postgis -U postgres -d postgres \
        -tAc "SELECT 1 FROM pg_database \
              WHERE datname='airflow'" \
        | grep -q 1; then
        echo "Database 'airflow' exists."
    else
        echo "Creating database 'airflow'..."
        PGPASSWORD=postgres psql \
            -h postgis -U postgres -d postgres \
            -c "CREATE DATABASE airflow;"
        echo "Database 'airflow' created."
    fi

# Perform project setup.
setup:
    #!/usr/bin/env bash
    set -aeo pipefail
    if [ ! -f .env ]; then
        cp .env.example .env
    fi
    mkdir -p temp
    mkdir -p .airflow
    if [ ! -f .airflow/simple_auth_manager_passwords.json ]; then
        echo '{"admin": "airflow"}' > .airflow/simple_auth_manager_passwords.json
        echo "Created .airflow/simple_auth_manager_passwords.json with default credentials"
    fi
    just ensure-databases
    uv sync
    uv pip install -e .

# Run tests.
test:
    #!/usr/bin/env bash
    set -aeo pipefail
    uv run pytest tests/
    uv run ruff check gardenflow/ tests/
    uv run ruff format --check gardenflow/ tests/
