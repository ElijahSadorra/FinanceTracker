import json
from pathlib import Path
from typing import Any, Dict

MAPPINGS_DIR = Path(__file__).resolve().parent / "providers" / "mappings"


def load_mapping(provider: str) -> Dict[str, Any]:
    provider_path = MAPPINGS_DIR / f"{provider}.json"
    if provider_path.exists():
        return json.loads(provider_path.read_text(encoding="utf-8"))

    default_path = MAPPINGS_DIR / "generic.json"
    if default_path.exists():
        return json.loads(default_path.read_text(encoding="utf-8"))

    raise FileNotFoundError("No CSV mapping configuration found.")
