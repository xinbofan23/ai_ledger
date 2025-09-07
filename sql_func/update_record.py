import os, re, uuid, pymysql
from typing import Optional, List, Dict
from datetime import datetime
from dateutil import parser
from zoneinfo import ZoneInfo
from decimal import Decimal, InvalidOperation
from .db_config import *

_LOCAL_DT_RE = re.compile(r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$")  # YYYY-MM-DD HH:MM:SS
_LOCAL_DAY_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")                   # YYYY-MM-DD

USER_ID = 1

def update_record(
    record_id: str,
    new_amount: str = "",           
    new_time_local: str = "",      
    new_category: str = "",   
    new_description: str = ""  
) -> dict:

    
    if not record_id or not record_id.strip():
        return {"ok": False, "error": "record_id required"}

    sets, args = [], []

    if new_amount.strip():
        try:
            amt = Decimal(str(new_amount)).quantize(Decimal("0.01"))
            if amt <= 0:
                return {"ok": False, "error": "Amount must be > 0"}
            sets.append("amount=%s")
            args.append(f"{amt:.2f}")
        except (InvalidOperation, ValueError, TypeError):
            return {"ok": False, "error": "Invalid new_amount"}

    if new_time_local.strip():
        if not _LOCAL_DT_RE.match(new_time_local):
            return {"ok": False, "error": "new_time_local must be 'YYYY-MM-DD HH:MM:SS'"}
        sets.append("occurred_time=%s")
        args.append(new_time_local)

    if new_category.strip():
        sets.append("category=%s")
        args.append(new_category.strip())

    if new_description != "":
        desc = new_description.strip()
        sets.append("description=%s")
        args.append(desc if desc else None)

    if not sets:
        return {"ok": False, "error": "No fields to update"}

    try:
        with pymysql.connect(**DB_CONFIG) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT record_id, user_id, amount, occurred_time, description, category "
                    "FROM records WHERE user_id=%s AND record_id=%s",
                    (USER_ID, record_id)
                )
                before = cur.fetchone()
                if not before:
                    return {"ok": False, "error": "Record not found for this user"}

                sql_update = f"UPDATE records SET {', '.join(sets)} WHERE user_id=%s AND record_id=%s"
                cur.execute(sql_update, args + [USER_ID, record_id])

                cur.execute(
                    "SELECT record_id, user_id, amount, occurred_time, description, category "
                    "FROM records WHERE user_id=%s AND record_id=%s",
                    (USER_ID, record_id)
                )
                after = cur.fetchone()
                conn.commit()

        before["amount"] = f"{Decimal(str(before['amount'])):.2f}"
        after["amount"]  = f"{Decimal(str(after['amount'])):.2f}"
        return {"ok": True, "before": before, "after": after}
    except Exception as e:
        return {"ok": False, "error": str(e)}

