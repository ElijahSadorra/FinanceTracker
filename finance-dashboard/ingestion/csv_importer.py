import csv
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

from ingestion.config import load_mapping
from ingestion.db import get_connection
from ingestion.hashing import compute_import_hash, dedupe_records


class MappingError(ValueError):
    pass


def _get_column(row: Dict[str, str], column: Optional[str]) -> str:
    if not column:
        return ""
    return row.get(column, "").strip()


def _parse_datetime(raw: str, date_format: str) -> datetime:
    if not raw:
        raise MappingError("Missing datetime value in CSV row.")
    parsed = datetime.strptime(raw, date_format)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed


def _parse_amount(raw: str) -> Decimal:
    if not raw:
        raise MappingError("Missing amount value in CSV row.")
    cleaned = raw.replace(",", "").strip()
    try:
        return Decimal(cleaned).quantize(Decimal("0.01"))
    except InvalidOperation as exc:
        raise MappingError(f"Invalid amount value: {raw}") from exc


def _load_csv_rows(csv_path: Path) -> Iterable[Dict[str, str]]:
    with csv_path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames:
            raise MappingError("CSV file missing header row.")
        for row in reader:
            yield row


def _normalise_rows(
    rows: Iterable[Dict[str, str]],
    provider: str,
    account_name: str,
    mapping: Dict[str, Any],
) -> List[Dict[str, Any]]:
    date_column = mapping.get("date_column")
    date_format = mapping.get("date_format", "%Y-%m-%d")
    amount_column = mapping.get("amount_column")
    currency_column = mapping.get("currency_column")
    currency_default = mapping.get("currency")
    merchant_column = mapping.get("merchant_column")
    description_column = mapping.get("description_column")
    transaction_id_column = mapping.get("transaction_id_column")
    amount_multiplier = Decimal(str(mapping.get("amount_multiplier", 1)))

    if not date_column or not amount_column:
        raise MappingError("CSV mapping must include date_column and amount_column.")

    normalised: List[Dict[str, Any]] = []
    for row in rows:
        raw_date = _get_column(row, date_column)
        raw_amount = _get_column(row, amount_column)
        if not raw_date or not raw_amount:
            continue
        parsed_date = _parse_datetime(raw_date, date_format)
        parsed_amount = _parse_amount(raw_amount) * amount_multiplier
        currency_value = _get_column(row, currency_column) or currency_default
        if not currency_value:
            raise MappingError("Currency missing and no default provided in mapping.")

        record = {
            "transaction_id": _get_column(row, transaction_id_column),
            "source_provider": provider,
            "account_name": account_name,
            "account_type": mapping.get("account_type", "checking"),
            "datetime": parsed_date.isoformat(),
            "amount": str(parsed_amount),
            "currency": currency_value,
            "merchant": _get_column(row, merchant_column),
            "description": _get_column(row, description_column),
        }
        record["import_hash"] = compute_import_hash(record)
        normalised.append(record)

    return normalised


def _ensure_account(cursor, provider: str, account_name: str, account_type: str, currency: str) -> str:
    cursor.execute(
        """
        SELECT id FROM accounts WHERE provider = %s AND name = %s
        """,
        (provider, account_name),
    )
    result = cursor.fetchone()
    if result:
        return result[0]

    cursor.execute(
        """
        INSERT INTO accounts (provider, name, type, currency)
        VALUES (%s, %s, %s, %s)
        RETURNING id
        """,
        (provider, account_name, account_type, currency),
    )
    return cursor.fetchone()[0]


def import_csv(provider: str, account_name: str, csv_path: str) -> None:
    mapping = load_mapping(provider)
    csv_file = Path(csv_path)
    if not csv_file.exists():
        raise FileNotFoundError(f"CSV file not found: {csv_path}")

    rows = list(_load_csv_rows(csv_file))
    normalised = _normalise_rows(rows, provider, account_name, mapping)
    unique_records = dedupe_records(normalised)

    connection = get_connection()
    connection.autocommit = False

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO import_runs (source_provider, status, row_count)
                VALUES (%s, %s, %s)
                RETURNING id
                """,
                (provider, "started", 0),
            )
            import_run_id = cursor.fetchone()[0]

            if not unique_records:
                cursor.execute(
                    """
                    UPDATE import_runs
                    SET status = %s, row_count = %s, finished_at = NOW()
                    WHERE id = %s
                    """,
                    ("completed", 0, import_run_id),
                )
                connection.commit()
                return

            inserted = 0
            account_id = _ensure_account(
                cursor,
                provider,
                account_name,
                mapping.get("account_type", "checking"),
                mapping.get("currency", "GBP") or unique_records[0]["currency"],
            )

            for record in unique_records:
                cursor.execute(
                    """
                    INSERT INTO transactions (
                        transaction_id,
                        source_provider,
                        account_id,
                        account_name,
                        account_type,
                        datetime,
                        amount,
                        currency,
                        merchant,
                        description,
                        import_hash,
                        import_run_id
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (import_hash) DO NOTHING
                    """,
                    (
                        record["transaction_id"],
                        record["source_provider"],
                        account_id,
                        record["account_name"],
                        record["account_type"],
                        record["datetime"],
                        record["amount"],
                        record["currency"],
                        record["merchant"],
                        record["description"],
                        record["import_hash"],
                        import_run_id,
                    ),
                )
                if cursor.rowcount == 1:
                    inserted += 1

            cursor.execute(
                """
                UPDATE import_runs
                SET status = %s, row_count = %s, finished_at = NOW()
                WHERE id = %s
                """,
                ("completed", inserted, import_run_id),
            )

        connection.commit()
    except Exception as exc:
        connection.rollback()
        with connection.cursor() as cursor:
            cursor.execute(
                """
                UPDATE import_runs
                SET status = %s, error_message = %s, finished_at = NOW()
                WHERE id = (
                    SELECT id FROM import_runs
                    WHERE source_provider = %s
                    ORDER BY started_at DESC
                    LIMIT 1
                )
                """,
                ("failed", str(exc), provider),
            )
            connection.commit()
        raise
    finally:
        connection.close()
