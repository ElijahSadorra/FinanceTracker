from ingestion.hashing import dedupe_records


def test_dedupe_records_removes_duplicates():
    records = [
        {"import_hash": "hash-1", "amount": "10"},
        {"import_hash": "hash-1", "amount": "10"},
        {"import_hash": "hash-2", "amount": "20"},
    ]

    unique = dedupe_records(records)

    assert len(unique) == 2
    assert {record["import_hash"] for record in unique} == {"hash-1", "hash-2"}
