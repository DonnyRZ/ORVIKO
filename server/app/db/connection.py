from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path
import sqlite3
from typing import Iterator

BASE_DIR = Path(__file__).resolve().parents[3]
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "tiktok_slide.db"
EMBEDS_DIR = DATA_DIR / "embeds"
RESULTS_DIR = DATA_DIR / "results"


@contextmanager
def db_connection() -> Iterator[sqlite3.Connection]:
  conn = sqlite3.connect(DB_PATH)
  conn.row_factory = sqlite3.Row
  conn.execute("PRAGMA busy_timeout=5000;")
  conn.execute("PRAGMA foreign_keys=ON;")
  try:
    yield conn
    conn.commit()
  finally:
    conn.close()
