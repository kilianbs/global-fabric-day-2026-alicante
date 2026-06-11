"""Validación ligera del repo antes de mergear a main.

- parameter.yml es YAML válido y solo usa claves soportadas.
- Cada carpeta de ítem en workspace/ contiene un archivo .platform.
"""

import sys
from pathlib import Path

import yaml

WORKSPACE_DIR = Path(__file__).resolve().parent.parent / "workspace"
ALLOWED_KEYS = {"find_replace", "key_value_replace", "spark_pool"}


def validate_parameter_file() -> list[str]:
    errors = []
    param_file = WORKSPACE_DIR / "parameter.yml"
    if not param_file.exists():
        return [f"No existe {param_file}"]
    data = yaml.safe_load(param_file.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        return ["parameter.yml está vacío o no es un mapping YAML válido"]
    unknown = set(data) - ALLOWED_KEYS
    if unknown:
        errors.append(f"Claves no soportadas en parameter.yml: {sorted(unknown)}")
    for entry in data.get("find_replace", []):
        if "find_value" not in entry or "replace_value" not in entry:
            errors.append(f"find_replace incompleto: {entry}")
    for entry in data.get("key_value_replace", []):
        if "find_key" not in entry or "replace_value" not in entry:
            errors.append(f"key_value_replace incompleto: {entry}")
    return errors


def validate_item_folders() -> list[str]:
    errors = []
    for folder in WORKSPACE_DIR.iterdir():
        if folder.is_dir() and "." in folder.name:
            if not (folder / ".platform").exists():
                errors.append(f"Falta .platform en {folder.name}")
    return errors


if __name__ == "__main__":
    all_errors = validate_parameter_file() + validate_item_folders()
    for err in all_errors:
        print(f"ERROR: {err}")
    if all_errors:
        sys.exit(1)
    print("Validación OK")
