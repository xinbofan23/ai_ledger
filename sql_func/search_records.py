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

def search_records(
    text: str = "",                
    datetime_from: str = "",  
    datetime_to: str = "",   
    category: str = "",             
    amount_exact: str = "",        
) -> dict:
    print("search_records", USER_ID, text, datetime_from, datetime_to, category, amount_exact )
    where = ["user_id=%s"]
    args: List = [USER_ID]

    if text.strip():
        like = f"%{text.strip()}%"
        where.append("(description LIKE %s OR category LIKE %s)")
        args.extend([like, like])

    if category.strip():
        where.append("category=%s")
        args.append(category.strip())

    if amount_exact.strip():
        try:
            amt = Decimal(str(amount_exact)).quantize(Decimal("0.01"))
            where.append("amount=%s")
            args.append(f"{amt:.2f}")
        except (InvalidOperation, ValueError, TypeError):
            return {"ok": False, "error": "Invalid amount_exact"}

    if datetime_from.strip():
        if not _LOCAL_DT_RE.match(datetime_from):
            return {"ok": False, "error": "datetime_from must be 'YYYY-MM-DD HH:MM:SS'"}
        where.append("occurred_time >= %s")
        args.append(datetime_from)

    if datetime_to.strip():
        if not _LOCAL_DT_RE.match(datetime_to):
            return {"ok": False, "error": "datetime_to must be 'YYYY-MM-DD HH:MM:SS'"}
        where.append("occurred_time <= %s")
        args.append(datetime_to)

    sql = f"""
        SELECT record_id, user_id, amount, occurred_time, description, category
        FROM records
        WHERE {' AND '.join(where)}
        ORDER BY occurred_time DESC
        LIMIT 10
    """


    try:
        with pymysql.connect(**DB_CONFIG) as conn:
            with conn.cursor() as cur:
                cur.execute(sql, args)
                rows = cur.fetchall()
        for r in rows:
            r["amount"] = f"{Decimal(str(r['amount'])):.2f}"
            print(rows)
        return {"ok": True, "records": rows}
    except Exception as e:
        return {"ok": False, "error": str(e)}
