from __future__ import annotations

import sqlite3

from app.db.connection import DATA_DIR, DB_PATH, EMBEDS_DIR, RESULTS_DIR


def init_db() -> None:
  DATA_DIR.mkdir(parents=True, exist_ok=True)
  EMBEDS_DIR.mkdir(parents=True, exist_ok=True)
  RESULTS_DIR.mkdir(parents=True, exist_ok=True)
  conn = sqlite3.connect(DB_PATH)
  try:
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA busy_timeout=5000;")
    conn.execute("PRAGMA foreign_keys=OFF;")
    conn.execute(
      """
      CREATE TABLE IF NOT EXISTS slides (
        id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        text TEXT NOT NULL,
        design TEXT NOT NULL,
        quantity INTEGER NOT NULL DEFAULT 1,
        aspect_ratio TEXT NOT NULL DEFAULT '9:16',
        selected_result_id TEXT,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
      )
      """
    )
    if (
      _column_exists(conn, "slides", "name")
      or _column_exists(conn, "slides", "position")
      or _column_exists(conn, "slides", "subtitle")
      or not _column_exists(conn, "slides", "aspect_ratio")
    ):
      _migrate_slides_table(conn)
    conn.execute(
      """
      CREATE TABLE IF NOT EXISTS slide_results (
        id TEXT PRIMARY KEY,
        slide_id TEXT NOT NULL,
        title TEXT NOT NULL,
        note TEXT NOT NULL,
        tone TEXT NOT NULL,
        status TEXT NOT NULL,
        image_path TEXT,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        FOREIGN KEY (slide_id) REFERENCES slides(id) ON DELETE CASCADE
      )
      """
    )
    conn.execute(
      """
      CREATE TABLE IF NOT EXISTS embed_assets (
        id TEXT PRIMARY KEY,
        slide_id TEXT NOT NULL,
        label TEXT NOT NULL,
        name TEXT NOT NULL,
        context TEXT NOT NULL DEFAULT '',
        file_path TEXT NOT NULL,
        mime_type TEXT NOT NULL,
        size INTEGER NOT NULL,
        created_at TEXT NOT NULL,
        FOREIGN KEY (slide_id) REFERENCES slides(id) ON DELETE CASCADE
      )
      """
    )
    if not _column_exists(conn, "embed_assets", "context"):
      conn.execute("ALTER TABLE embed_assets ADD COLUMN context TEXT NOT NULL DEFAULT ''")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_results_slide_id ON slide_results(slide_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_embeds_slide_id ON embed_assets(slide_id)")
    conn.execute(
      """
      CREATE TABLE IF NOT EXISTS script_knowledge_bases (
        id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        summary TEXT NOT NULL,
        data TEXT NOT NULL,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
      )
      """
    )
    conn.execute(
      """
      CREATE TABLE IF NOT EXISTS script_workspaces (
        id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        knowledge_base_id TEXT NOT NULL,
        knowledge_base_snapshot TEXT NOT NULL DEFAULT '{}',
        current_step TEXT NOT NULL DEFAULT 'task',
        active_profile_id TEXT NOT NULL DEFAULT '',
        task TEXT NOT NULL DEFAULT '',
        selected_source TEXT NOT NULL DEFAULT '',
        source_options TEXT NOT NULL DEFAULT '[]',
        observations TEXT NOT NULL DEFAULT '{}',
        moments TEXT NOT NULL DEFAULT '[]',
        observation_variant_index INTEGER NOT NULL DEFAULT 0,
        moment_variant_index INTEGER NOT NULL DEFAULT 0,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        FOREIGN KEY (knowledge_base_id) REFERENCES script_knowledge_bases(id) ON DELETE RESTRICT
      )
      """
    )
    if not _column_exists(conn, "script_workspaces", "knowledge_base_snapshot"):
      conn.execute("ALTER TABLE script_workspaces ADD COLUMN knowledge_base_snapshot TEXT NOT NULL DEFAULT '{}'")
    if not _column_exists(conn, "script_workspaces", "active_profile_id"):
      conn.execute("ALTER TABLE script_workspaces ADD COLUMN active_profile_id TEXT NOT NULL DEFAULT ''")
    if not _column_exists(conn, "script_workspaces", "observation_variant_index"):
      conn.execute("ALTER TABLE script_workspaces ADD COLUMN observation_variant_index INTEGER NOT NULL DEFAULT 0")
    if not _column_exists(conn, "script_workspaces", "moment_variant_index"):
      conn.execute("ALTER TABLE script_workspaces ADD COLUMN moment_variant_index INTEGER NOT NULL DEFAULT 0")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_script_workspace_kb_id ON script_workspaces(knowledge_base_id)")
    conn.execute(
      """
      CREATE TABLE IF NOT EXISTS users (
        id TEXT PRIMARY KEY,
        google_sub TEXT NOT NULL UNIQUE,
        name TEXT NOT NULL DEFAULT '',
        email TEXT NOT NULL UNIQUE,
        picture TEXT NOT NULL DEFAULT '',
        auth_provider TEXT NOT NULL DEFAULT 'google',
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
      )
      """
    )
    conn.execute("CREATE INDEX IF NOT EXISTS idx_users_google_sub ON users(google_sub)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)")
    conn.execute(
      """
      CREATE TABLE IF NOT EXISTS payments (
        id TEXT PRIMARY KEY,
        user_id TEXT NOT NULL,
        order_id TEXT NOT NULL UNIQUE,
        plan TEXT NOT NULL,
        gross_amount INTEGER NOT NULL,
        currency TEXT NOT NULL DEFAULT 'IDR',
        status TEXT NOT NULL DEFAULT 'created',
        snap_token TEXT NOT NULL DEFAULT '',
        snap_redirect_url TEXT NOT NULL DEFAULT '',
        midtrans_transaction_id TEXT NOT NULL DEFAULT '',
        midtrans_order_id TEXT NOT NULL DEFAULT '',
        raw_notification TEXT NOT NULL DEFAULT '{}',
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
      )
      """
    )
    conn.execute("CREATE INDEX IF NOT EXISTS idx_payments_user_id ON payments(user_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_payments_status ON payments(status)")
    conn.commit()
  finally:
    conn.execute("PRAGMA foreign_keys=ON;")
    conn.close()


def _column_exists(conn: sqlite3.Connection, table: str, column: str) -> bool:
  rows = conn.execute(f"PRAGMA table_info({table})").fetchall()
  return any(row[1] == column for row in rows)


def _migrate_slides_table(conn: sqlite3.Connection) -> None:
  has_aspect_ratio = _column_exists(conn, "slides", "aspect_ratio")
  conn.execute(
    """
    CREATE TABLE slides_v2 (
      id TEXT PRIMARY KEY,
      title TEXT NOT NULL,
      text TEXT NOT NULL,
      design TEXT NOT NULL,
      quantity INTEGER NOT NULL DEFAULT 1,
      aspect_ratio TEXT NOT NULL DEFAULT '9:16',
      selected_result_id TEXT,
      created_at TEXT NOT NULL,
      updated_at TEXT NOT NULL
    )
    """
  )
  conn.execute(
    (
      """
      INSERT INTO slides_v2 (id, title, text, design, quantity, aspect_ratio, selected_result_id, created_at, updated_at)
      SELECT id, title, text, design, quantity, COALESCE(aspect_ratio, '9:16'), selected_result_id, created_at, updated_at
      FROM slides
      ORDER BY created_at ASC
      """
      if has_aspect_ratio
      else """
      INSERT INTO slides_v2 (id, title, text, design, quantity, aspect_ratio, selected_result_id, created_at, updated_at)
      SELECT id, title, text, design, quantity, '9:16', selected_result_id, created_at, updated_at
      FROM slides
      ORDER BY created_at ASC
      """
    )
  )
  conn.execute("DROP TABLE slides")
  conn.execute("ALTER TABLE slides_v2 RENAME TO slides")
