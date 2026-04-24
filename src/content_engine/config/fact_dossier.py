from pathlib import Path
from typing import Any

import yaml


def load_fact_dossier(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as fh:
        return yaml.safe_load(fh)
