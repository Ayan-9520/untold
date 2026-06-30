#!/usr/bin/env python3
"""Export FastAPI OpenAPI schema to docs/openapi/untold-api.json."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = ROOT / "docs" / "openapi"
OUT_FILE = OUT_DIR / "untold-api.json"


def main() -> int:
    sys.path.insert(0, str(ROOT / "backend"))
    from app.main import app  # noqa: WPS433

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    spec = app.openapi()
    OUT_FILE.write_text(json.dumps(spec, indent=2), encoding="utf-8")
    print(f"Wrote {OUT_FILE} ({OUT_FILE.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
