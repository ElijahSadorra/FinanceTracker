import hashlib
from typing import Dict


def _normalise_text(value: str) -> str:
    return " ".join(value.strip().lower().split())


def compute_import_hash(record: Dict[str, str]) -> str:
    parts = [
        _normalise_text(str(record.get("source_provider", ""))),
        _normalise_text(str(record.get("account_name", ""))),
        _normalise_text(str(record.get("datetime", ""))),
        _normalise_text(str(record.get("amount", ""))),
        _normalise_text(str(record.get("currency", ""))),
        _normalise_text(str(record.get("merchant", ""))),
        _normalise_text(str(record.get("description", ""))),
        _normalise_text(str(record.get("transaction_id", ""))),
    ]
    raw = "|".join(parts)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def dedupe_records(records: list[Dict[str, str]]) -> list[Dict[str, str]]:
    seen: set[str] = set()
    unique: list[Dict[str, str]] = []
    for record in records:
        record_hash = record["import_hash"]
        if record_hash in seen:
            continue
        seen.add(record_hash)
        unique.append(record)
    return unique
