"""Run Alembic migrations programmatically."""

import logging
from pathlib import Path

from alembic import command
from alembic.config import Config

logger = logging.getLogger("untold")

_BACKEND_ROOT = Path(__file__).resolve().parents[2]


def run_migrations() -> None:
    """Apply all pending Alembic migrations up to head."""
    alembic_ini = _BACKEND_ROOT / "alembic.ini"
    if not alembic_ini.exists():
        raise FileNotFoundError(f"Alembic config not found: {alembic_ini}")

    cfg = Config(str(alembic_ini))
    cfg.set_main_option("script_location", str(_BACKEND_ROOT / "alembic"))
    logger.info("Running database migrations...")
    command.upgrade(cfg, "head")
    logger.info("Database migrations complete")
