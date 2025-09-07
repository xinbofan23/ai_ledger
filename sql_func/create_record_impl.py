import os, re, uuid, pymysql
from typing import Optional, List, Dict
from datetime import datetime
from dateutil import parser
from zoneinfo import ZoneInfo
from decimal import Decimal, InvalidOperation
from .db_config import *


USER_ID = 1
def _create_record_impl(user_id: int, amount_raw, time_utc_iso: str, category: str, description: Optional[str]):
    # amount
    try:
        amt = Decimal(str(amount_raw)).quantize(Decimal("0.01"))
    except (InvalidOperation, ValueError, TypeError):
        return {"ok": False, "error": "Invalid amount"}
    if amt <= 0:
        return {"ok": False, "error": "Amount must be > 0"}

    # time
    iso = (time_utc_iso or "").strip()
    if not (iso.endswith("Z") and "T" in iso):
        return {"ok": False, "error": "time_utc_iso must look like 'YYYY-MM-DDTHH:MM:SSZ'"}
    occurred_time = iso.replace("T", " ").rstrip("Z").strip()

    cat = (category or "Other").strip()[:128] or "Other"
    desc = (description or "").strip()[:512] or None

    record_id = str(uuid.uuid4())
    sql = """
        INSERT INTO records (record_id, USER_ID, amount, occurred_time, description, category)
        VALUES (%s, %s, %s, %s, %s, %s)
    """
    try:
        with pymysql.connect(**DB_CONFIG) as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (record_id, USER_ID, f"{amt:.2f}", occurred_time, desc, cat))
            conn.commit()
        return {
            "ok": True,
            "record": {
                "record_id": record_id,
                "user_id": USER_ID,
                "amount": f"{amt:.2f}",
                "occurred_time": occurred_time,
                "category": cat,
                "description": desc,
            },
        }
    except Exception as e:
        return {"ok": False, "error": str(e)}