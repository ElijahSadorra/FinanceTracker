# 🧮 Open-Source Personal Finance Automation Dashboard

A self-hosted, open-source system to automatically ingest, normalise, categorise, and visualise personal finance data across UK bank accounts and investment platforms. The system aggregates transactions into a unified ledger, exposes them via a mobile-friendly dashboard, and keeps ingestion, storage, processing, and visualisation clearly separated.

## Architecture Overview

**High-level architecture diagram (text):**

```
[Bank/Investment APIs + Statement Imports]
                 |
                 v
         [Ingestion Services]
   (Open Banking, Starling, T212,
      CSV/OFX/PDF Importers)
                 |
                 v
          [Staging Tables]
                 |
                 v
   [Normalisation + Dedup + Rules]
                 |
                 v
         [Unified Ledger DB]
                 |
        ---------------------
        |                   |
        v                   v
[Dashboard Read-Only User]  [Ops/Admin Tools]
(Metabase/Superset)         (Rules, Imports)
```

**Design intent**
- Clear separation: ingestion → staging → processing → unified ledger → read-only analytics.
- Idempotent imports with deterministic hashes for safe re-ingestion.
- Open-source stack for self-hosted deployments.

## Data Sources & Ingestion

**Sources**
- **NatWest**: current, credit, savings via Open Banking.
- **Starling**: joint current + savings/investments via Starling API.
- **Trading 212**: Stocks & Shares ISA, Cash ISA via Trading 212 API.
- **Tembo**: Cash ISA, Lifetime ISA via statement import (CSV/OFX/PDF).

**Ingestion principles**
- Prefer official APIs and Open Banking consent-based access.
- No browser scraping or credential-stuffing.
- Scheduled ingestion (hourly/daily) with idempotent re-runs.
- Import hash + provider transaction IDs to prevent duplicates.

**Pipeline outline**
1. **Fetch**: Pull API data or parse statements into raw import records.
2. **Stage**: Store raw payloads + metadata (source, import run, checksum).
3. **Normalize**: Map fields to canonical transaction shape.
4. **Deduplicate**: Apply `import_hash` + provider IDs.
5. **Load**: Write to unified ledger tables.

## Database Design

**Core schema (normalized)**

**transactions**
- `id` (uuid)
- `transaction_id` (provider-specific)
- `source_provider` (natwest, starling, t212, tembo)
- `account_id` (FK → accounts)
- `account_name`
- `account_type` (credit, debit, savings, isa, lisa)
- `datetime`
- `amount` (signed)
- `currency`
- `merchant`
- `description`
- `category_id` (FK → categories)
- `tags` (text[])
- `import_hash` (unique)
- `created_at`

**accounts**
- `id` (uuid)
- `provider`
- `name`
- `type`
- `currency`
- `account_identifier` (masked)

**categories**
- `id` (uuid)
- `name`
- `parent_id` (nullable for hierarchy)

**category_rules**
- `id` (uuid)
- `priority` (int)
- `merchant_match` (nullable)
- `description_regex` (nullable)
- `amount_min` / `amount_max` (nullable)
- `account_type` (nullable)
- `category_id` (FK → categories)

**balance_snapshots**
- `id` (uuid)
- `account_id` (FK)
- `datetime`
- `balance`
- `currency`

**import_runs**
- `id` (uuid)
- `source_provider`
- `started_at`
- `completed_at`
- `status`
- `row_count`
- `checksum`

**investments** (optional specialized ledger table)
- `id` (uuid)
- `transaction_id`
- `instrument`
- `side` (buy/sell/dividend)
- `quantity`
- `price`
- `fees`
- `currency`

**Notes**
- `import_hash` is a stable hash of provider + transaction_id + datetime + amount + description.
- Transfers between own accounts use a `transfer_group_id` (optional extension) to link both sides.

## Categorisation Engine

**Rule-based first** (deterministic and auditable):
- Ordered rules evaluated by priority.
- Matching supports merchant string, regex on description, amount ranges, and account type.
- Rules live in the database and can be edited via a simple admin UI or configuration file.

**Manual overrides**
- Users can manually override a transaction’s category.
- Re-imports never overwrite manual overrides.
- Override state stored directly on the transaction record.

## Dashboard Design

**Recommended tool**: Metabase (open-source, simple to host). Superset as an alternative.

**Key dashboards**
1. **Monthly Spend by Category** (bar/pie)
2. **Spend Over Time** (line)
3. **Net Worth Over Time** (line)
4. **Cashflow (Income vs Expenses)** (stacked/line)
5. **Transactions Table** (filterable)

**Filters**
- Date range
- Account
- Category
- Merchant
- Tags

**UX requirements**
- Mobile-friendly
- Read-only by default
- Auth protected

## Security Considerations

- Secrets stored via environment variables.
- OAuth tokens encrypted at rest.
- Dashboard uses a **read-only database user**.
- Ingestion services isolated from analytics UI.
- No hard-coded credentials.

## Implementation Roadmap

1. **Database & schema**: Build PostgreSQL schema + migrations.
2. **Manual imports**: CSV/OFX/PDF pipeline for Tembo and fallback ingestion.
3. **Dashboard MVP**: Metabase + sample data.
4. **Starling API ingestion**.
5. **Trading 212 API ingestion**.
6. **Open Banking integration** (NatWest + aggregator).
7. **Categorisation rules engine** + admin UI.
8. **Scheduling & automation** (cron / background jobs).
9. **Hardening**: audit logs, backup strategy, monitoring.

## Phase 1: Database

The Phase 1 schema and seed data live under `finance-dashboard/sql/` and are applied automatically when Postgres first initializes using `docker/postgres/initdb.d`. This is a simple MVP migration strategy (schema-on-init) that is sufficient until a dedicated migration tool is added in a later phase.

**Run Phase 1**
1. Copy the example environment file and adjust credentials:
   - `cp finance-dashboard/.env.example finance-dashboard/.env`
2. Start Postgres (and Adminer UI) locally:
   - `docker compose -f finance-dashboard/docker-compose.yml up -d`
3. Verify schema is loaded:
   - `docker compose -f finance-dashboard/docker-compose.yml exec -T postgres psql -U $POSTGRES_USER -d $POSTGRES_DB -c "\\dt"`

Adminer (optional) will be available at `http://localhost:8080` unless you override `ADMINER_PORT`.

## Optional Enhancements

- ML-assisted categorisation (suggestions, not auto-apply).
- Budgeting and envelope-style views.
- Alerts (overspend, low balance, threshold-based).
- Forecasting (cashflow projection).
- Net worth goals + progress tracking.
- Export to CSV/Excel.
- Mobile PWA.

---

**Non-goals**
- Becoming a regulated AISP.
- Credential scraping or browser automation.
- Real-time transaction processing (daily/hourly is sufficient).

**License**
- MIT (or similar permissive open-source license).

**AI assistant guidance**
- Prefer simplicity over abstraction.
- Keep ingestion, processing, and visualisation clearly separated.
- Assume UK financial context.
