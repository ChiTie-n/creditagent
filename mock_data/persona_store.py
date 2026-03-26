import json
from pathlib import Path
from typing import Any

from mock_data.personas import PERSONAS


ROOT = Path(__file__).resolve().parent.parent
CUSTOM_PERSONAS_PATH = ROOT / "data" / "custom_personas.json"


def _ensure_parent_dir() -> None:
    CUSTOM_PERSONAS_PATH.parent.mkdir(parents=True, exist_ok=True)


def load_custom_personas() -> dict[str, dict[str, Any]]:
    if not CUSTOM_PERSONAS_PATH.exists():
        return {}

    with CUSTOM_PERSONAS_PATH.open("r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, dict):
        raise ValueError("custom_personas.json must contain a JSON object")

    return data


def save_custom_personas(personas: dict[str, dict[str, Any]]) -> None:
    _ensure_parent_dir()
    with CUSTOM_PERSONAS_PATH.open("w", encoding="utf-8") as f:
        json.dump(personas, f, ensure_ascii=False, indent=2)


def hydrate_personas() -> None:
    PERSONAS.update(load_custom_personas())


def list_custom_personas() -> dict[str, dict[str, Any]]:
    return {
        borrower_id: persona
        for borrower_id, persona in PERSONAS.items()
        if borrower_id.startswith("custom_")
    }


def next_custom_borrower_id() -> str:
    existing_ids = [
        borrower_id
        for borrower_id in PERSONAS.keys()
        if borrower_id.startswith("custom_")
    ]
    max_suffix = 0

    for borrower_id in existing_ids:
        suffix = borrower_id.removeprefix("custom_")
        if suffix.isdigit():
            max_suffix = max(max_suffix, int(suffix))

    return f"custom_{max_suffix + 1:03d}"
