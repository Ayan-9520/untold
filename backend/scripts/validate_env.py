"""Validate environment configuration — run before deploy or in CI."""

import sys
from pathlib import Path

# Allow running as: python scripts/validate_env.py
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.core.config import get_settings


def main() -> int:
    try:
        settings = get_settings()
    except Exception as exc:
        print(f"Environment validation failed: {exc}", file=sys.stderr)
        return 1

    print(f"Environment OK: {settings.app_name} v{settings.app_version} [{settings.environment}]")
    if settings.seed_database:
        print("  SEED_DATABASE=true (admin + demo data will be seeded on startup)")
    if settings.is_production:
        print("  Production mode — docs disabled, strict validation active")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
