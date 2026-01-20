from ingestion.hashing import compute_import_hash


def test_compute_import_hash_is_deterministic():
    record = {
        "source_provider": "sample_bank",
        "account_name": "Main",
        "datetime": "2024-01-05T00:00:00+00:00",
        "amount": "-54.32",
        "currency": "GBP",
        "merchant": "Acme Grocers",
        "description": "Weekly shop",
        "transaction_id": "TXN-1001",
    }

    first = compute_import_hash(record)
    second = compute_import_hash(record)

    assert first == second
