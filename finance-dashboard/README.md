# Finance Dashboard (Personal, UK)

Self-hosted personal finance dashboard using PostgreSQL for storage and a Python ingestion CLI. All components are open-source and run locally.

## Requirements

- Docker + Docker Compose
- Python 3.10+

## Phase 1: Database

### What this includes

- PostgreSQL schema and seed data.
- Docker Compose services for Postgres + Adminer.
- Simple init strategy (schema + seed applied at container init).

### How to run

```bash
docker compose up -d
```

## Phase 2: CSV Import

### What this includes

- Python ingestion CLI: `python -m ingestion import-csv`.
- Provider CSV mappings with a sample mapping and CSV.
- Deterministic import hashing and idempotent UPSERT logic.
- Import run tracking in `import_runs`.

### How to run

1. Start the database:

```bash
docker compose up -d
```

2. Install Python dependencies:

```bash
python -m venv .venv
```

PowerShell:

```powershell
.venv\\Scripts\\Activate.ps1
```

Bash:

```bash
source .venv/bin/activate
pip install -r ingestion/requirements.txt
```

3. Import the sample CSV:

```bash
python -m ingestion import-csv --provider sample_bank --account "Main" --file ingestion/providers/imports/samples/sample_bank.csv
```

### CSV mappings

Mappings live in `ingestion/providers/mappings/`. Add a new `<provider>.json` file that defines the column mappings and date format to match your export.
