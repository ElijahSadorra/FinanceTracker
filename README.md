🧮 Open-Source Personal Finance Automation Dashboard

A self-hosted, open-source system to automatically ingest, normalise, categorise, and visualise personal finance data across UK bank accounts and investment platforms.

This project aggregates transactions into a single unified ledger, then exposes them via a mobile-friendly web dashboard with charts and tables.

🎯 Goals

Fully open-source stack

No screen scraping or credential automation

Browser-based dashboard (desktop + mobile)

Automated ingestion where possible

Manual import fallback where APIs are unavailable

Clear, auditable data model

Simple to self-host using Docker

🧩 Supported Accounts
Banking

NatWest

Credit Card

Debit / Current Account

Savings Account

Starling

Joint Current Account

Investments / Savings

Trading 212

Stocks & Shares ISA

Cash ISA

Tembo

Cash ISA

Lifetime ISA (LISA)

🧰 Tech Stack
Core

PostgreSQL – primary datastore

Docker + Docker Compose – local & server deployment

Python or C# – ingestion services

APIs

Open Banking (via aggregator or direct where possible)

Starling Bank Developer API

Trading 212 Public API

Dashboard

Metabase (preferred)
or

Apache Superset

🔄 Data Ingestion Strategy
1. Open Banking (Preferred)

Used for NatWest accounts where available

Consent-based, read-only

Tokens refreshed securely

2. Official APIs

Starling: personal access token

Trading 212: API key

3. Statement Import (Fallback)

CSV / OFX / PDF

Used for Tembo ISAs and any unsupported accounts

Must support safe re-imports

🗃️ Unified Ledger Schema

All data is normalised into a single transactions table.

Minimum fields:

id
transaction_id
source_provider
account_name
account_type
datetime
amount
currency
merchant
description
category
tags[]
import_hash
created_at


Additional tables:

accounts

categories

category_rules

balance_snapshots

import_runs

Requirements

Idempotent imports

Duplicate detection via hash

Transfers between own accounts supported

Investment events supported (buy/sell/dividend)

🏷️ Categorisation Engine
Rule-Based First (Deterministic)

Rules can include:

Merchant name matching

Regex on description

Amount direction / thresholds

Account type context

Rules are:

Evaluated in order

Configurable via file or database

Overrideable per transaction

Manual overrides must never be overwritten by re-imports.

📊 Dashboard Requirements

Dashboards must include:

Charts

Monthly spend by category

Spend over time

Net worth over time

Income vs expenses (cashflow)

Tables

Full transaction ledger

Filterable by:

Date range

Account

Category

Merchant

Tags

UX

Mobile-friendly

Read-only by default

Auth protected

No write access from dashboard

🔐 Security Principles

No credentials in source code

All secrets via environment variables

OAuth tokens encrypted at rest

Database read-only user for dashboards

Ingestion services isolated from dashboard

🚀 Getting Started (High Level)

Clone repository

Configure .env

Start services with Docker Compose

Run ingestion jobs

Open dashboard in browser

Configure categories & dashboards

🛠️ Implementation Order (Recommended)

PostgreSQL schema

Manual CSV import pipeline

Dashboard with sample data

Starling API ingestion

Trading 212 API ingestion

Open Banking integration

Categorisation rules engine

Scheduling & automation

🗺️ Future Enhancements

ML-assisted categorisation

Budget tracking

Alerts (overspend, low balance)

Forecasting

Mobile PWA

Net-worth goals

Export to CSV/Excel

⚠️ Non-Goals

Becoming a regulated AISP

Selling this as a product

Credential scraping

Real-time transaction processing

📄 License

MIT (or similar permissive open-source license)

🤖 For AI Assistants (Codex / Copilot)

When generating code for this repository:

Prefer simplicity over abstraction

Write readable, auditable code

Avoid over-engineering

Keep ingestion, processing, and visualisation clearly separated

Assume UK financial context
