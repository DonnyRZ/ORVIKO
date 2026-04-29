"""Compatibility exports for the refactored database package.

New code should import from app.db.* directly.
"""

from app.db.connection import DATA_DIR, DB_PATH, EMBEDS_DIR, RESULTS_DIR, db_connection
from app.db.files import delete_file, save_embed_file, save_result_image
from app.db.migrations import init_db
from app.db.repositories.payments import (
  create_payment,
  get_payment,
  get_payment_by_order_id,
  update_payment_snap_details,
  update_payment_status,
)
from app.db.repositories.scripts import (
  create_script_knowledge_base,
  create_script_workspace,
  get_first_script_knowledge_base,
  get_first_script_workspace,
  get_latest_script_workspace,
  get_script_knowledge_base,
  get_script_workspace,
  list_script_knowledge_bases,
  list_script_workspaces,
  update_script_workspace,
)
from app.db.repositories.slides import (
  create_embed,
  create_result,
  create_slide,
  delete_embed,
  delete_result,
  delete_slide,
  get_embed,
  get_result,
  get_slide,
  list_embed_paths,
  list_embeds,
  list_result_paths,
  list_results,
  list_slides,
  select_result,
  update_embed,
  update_slide,
)
from app.db.repositories.users import (
  create_user,
  get_user_by_google_sub,
  get_user_by_id,
  update_user_by_google_sub,
  upsert_google_user,
)
