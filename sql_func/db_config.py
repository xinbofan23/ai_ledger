import os, re, uuid, pymysql
from typing import Optional, List, Dict
from datetime import datetime
from dateutil import parser
from zoneinfo import ZoneInfo
from decimal import Decimal, InvalidOperation


DB_CONFIG = {
    "host": os.getenv("DB_HOST", ""),
    "user": os.getenv("DB_USER", ""),
    "password": os.getenv("DB_PASSWORD", ""),
    "database": os.getenv("DB_NAME", ""),
    "charset": "utf8mb4",
    "cursorclass": pymysql.cursors.DictCursor,
}