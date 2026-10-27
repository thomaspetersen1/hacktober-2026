"""Snowflake / Snowpark session helper with stale-connection recovery."""

import logging
import threading

from snowflake.connector.errors import DatabaseError, OperationalError
from snowflake.snowpark import Session

from app.config import get_settings

logger = logging.getLogger(__name__)

_session: Session | None = None
_lock = threading.Lock()


def _build() -> Session:
    s = get_settings()
    if not s.snowflake_configured:
        raise RuntimeError("Snowflake is not configured; fill in .env at the repo root")
    params = {
        "account": s.snowflake_account,
        "user": s.snowflake_user,
        "password": s.snowflake_password,
        "role": s.snowflake_role,
        "warehouse": s.snowflake_warehouse,
        "database": s.snowflake_database,
        "schema": s.snowflake_schema,
    }
    return Session.builder.configs({k: v for k, v in params.items() if v}).create()


def get_session() -> Session:
    """Live session, rebuilt if the previous one died."""
    global _session
    if _session is not None:
        try:
            _session.sql("SELECT 1").collect()
            return _session
        except (DatabaseError, OperationalError):
            logger.warning("Snowflake session stale, reconnecting")
            _session = None
    with _lock:
        if _session is None:
            _session = _build()
    return _session


def run_query(sql: str) -> list:
    """Single entry point so concurrent requests never share a session race."""
    with _lock:
        return get_session().sql(sql).collect()
