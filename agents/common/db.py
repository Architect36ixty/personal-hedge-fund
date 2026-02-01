import os
import logging
from typing import Any, Dict, List, Optional
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger("db")


def get_supabase_client() -> Client:
    """Create and validate a Supabase client using environment variables.

    Raises ValueError if required configuration is missing.
    """
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")

    if not url or not key:
        raise ValueError("Supabase URL and Key must be set in environment variables.")

    return create_client(url, key)


def safe_upsert(table: str, records: List[Dict[str, Any]], on_conflict: Optional[str] = None) -> Any:
    """Upsert records into a table with error handling.

    This centralizes DB writes so we can add retries, logging, or auditing later.
    """
    if not records:
        logger.debug("safe_upsert called with empty records; skipping")
        return None

    client = get_supabase_client()
    try:
        if on_conflict:
            resp = client.table(table).upsert(records, on_conflict=on_conflict).execute()
        else:
            resp = client.table(table).upsert(records).execute()
        logger.info("Upserted %d records into %s", len(records), table)
        return resp
    except Exception as e:
        logger.exception("Supabase upsert error for table %s: %s", table, e)
        raise


def safe_insert(table: str, records: List[Dict[str, Any]]) -> Any:
    client = get_supabase_client()
    try:
        resp = client.table(table).insert(records).execute()
        logger.info("Inserted %d records into %s", len(records), table)
        return resp
    except Exception as e:
        logger.exception("Supabase insert error for table %s: %s", table, e)
        raise


def safe_select(table: str, filters: Optional[Dict[str, Any]] = None, limit: Optional[int] = None) -> List[Dict[str, Any]]:
    client = get_supabase_client()
    try:
        q = client.table(table).select("*")
        if filters:
            for k, v in filters.items():
                q = q.eq(k, v)
        if limit:
            q = q.limit(limit)
        resp = q.execute()
        return resp.data if hasattr(resp, 'data') else []
    except Exception as e:
        logger.exception("Supabase select error for table %s: %s", table, e)
        raise
