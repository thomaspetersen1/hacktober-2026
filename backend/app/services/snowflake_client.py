"""Snowflake / Snowpark session helper."""

from functools import lru_cache

from snowflake.snowpark import Session

from app.config import get_settings


@lru_cache
def get_session() -> Session:
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
