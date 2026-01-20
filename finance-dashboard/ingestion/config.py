import json
from pathlib import Path
from typing import Any, Dict

MAPPINGS_DIR = Path(__file__).resolve().parent / "providers" / "mappings"

def _validate_mapping(mapping: Dict[str, Any], source: Path) -> None:
    missing = [
        key
        for key in ("date_column", "amount_column")
        if not mapping.get(key)
    ]
    if missing:
        missing_list = ", ".join(missing)
        raise ValueError(
            f"Mapping {source.name} is missing required keys: {missing_list}"
        )

def _load_all_mappings() -> Dict[str, Dict[str, Any]]:
    mappings: Dict[str, Dict[str, Any]] = {}
    for mapping_path in sorted(MAPPINGS_DIR.glob("*.json")):
        mapping = json.loads(mapping_path.read_text(encoding="utf-8"))
        _validate_mapping(mapping, mapping_path)
        mappings[mapping_path.stem] = mapping
    return mappings

def load_mapping(provider: str) -> Dict[str, Any]:
    mappings = _load_all_mappings()
    if provider in mappings:
        return mappings[provider]
    if "generic" in mappings:
        return mappings["generic"]
    raise FileNotFoundError(f"No CSV mapping configuration found.\n These are the mappings: {mappings.keys()} ")