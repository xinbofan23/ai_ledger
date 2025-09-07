import os, re, uuid, pymysql
from typing import Optional, List, Dict
from datetime import datetime
from dateutil import parser
from zoneinfo import ZoneInfo
from decimal import Decimal, InvalidOperation
from sql_func.create_record_impl import _create_record_impl


LOCAL_TZ = ZoneInfo("America/New_York")
USER_ID = 1

def get_time_now():
    return datetime.now(LOCAL_TZ)

def _normalize_time_phrase(s: Optional[str]) -> Optional[str]:
    if not s: return s
    t = s.strip().lower()
    t = re.sub(r'\b(\d{1,2})\s*afternoon\b', r'\1 pm', t)
    t = re.sub(r'\bafternoon\s*(\d{1,2})\b', r'\1 pm', t)
    t = re.sub(r'\b(\d{1,2})\s*morning\b', r'\1 am', t)
    t = re.sub(r'\bmorning\s*(\d{1,2})\b', r'\1 am', t)
    t = re.sub(r'\b(\d{1,2})\s*evening\b', r'\1 pm', t)
    t = re.sub(r'\bevening\s*(\d{1,2})\b', r'\1 pm', t)
    t = re.sub(r'\b(\d{1,2})\s*night\b', r'\1 pm', t)
    t = re.sub(r'\bnight\s*(\d{1,2})\b', r'\1 pm', t)
    t = re.sub(r'\bnoon\b', '12 pm', t)
    t = re.sub(r'\bmidnight\b', '12 am', t)
    t = re.sub(r'\bmorning\b', '9 am', t)
    t = re.sub(r'\bafternoon\b', '3 pm', t)
    t = re.sub(r'\bevening\b', '7 pm', t)
    t = re.sub(r'\bnight\b', '9 pm', t)
    return t

def parse_datetime_iso(info: Optional[str] = None) -> str:
    """Return UTC ISO 'YYYY-MM-DDTHH:MM:SSZ'. If missing, use now()."""
    now_local = datetime.now(LOCAL_TZ)
    if not info or not str(info).strip():
        dt_local = now_local
    else:
        text = _normalize_time_phrase(info)
        try:
            dt = parser.parse(text, fuzzy=True, default=now_local)
        except Exception:
            dt = now_local
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=LOCAL_TZ)
        dt_local = dt
    return dt_local.astimezone(ZoneInfo("UTC")).strftime("%Y-%m-%dT%H:%M:%SZ")


def create_record(
    amount: str,        
    time_utc_iso: str, 
    category: str,
    description: Optional[str] = None,
) -> dict:
    return _create_record_impl(USER_ID, amount, time_utc_iso, category, description)


