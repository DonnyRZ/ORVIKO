from fastapi import APIRouter, HTTPException

from app.db.connection import db_connection
from app.db.repositories.scripts import (
  get_script_knowledge_base,
  list_script_workspaces,
  update_script_workspace,
)
from app.schemas.script import (
  ScriptGenerationRequest,
  ScriptHistoryResponse,
  ScriptMomentsUpdateRequest,
  ScriptObservationsUpdateRequest,
  ScriptSourceSelectionRequest,
  ScriptTaskUpdateRequest,
  ScriptWorkspaceResponse,
)
from app.services.script_service import (
  build_workspace_response_payload,
  create_new_script_workspace,
  detect_profile_id,
  ensure_script_workspace_seeded,
  generate_moments,
  generate_observations,
  get_script_workspace_bundle,
  shortlist_sources,
)

router = APIRouter(prefix="/script", tags=["script"])


def _load_workspace_and_kb() -> tuple[dict, dict]:
  bundle = get_script_workspace_bundle()
  return bundle["workspace"], bundle["knowledge_base"]


def _load_workspace_and_kb_by_id(workspace_id: str) -> tuple[dict, dict]:
  try:
    bundle = get_script_workspace_bundle(workspace_id)
  except ValueError:
    raise HTTPException(status_code=404, detail="Workspace script tidak ditemukan.") from None
  return bundle["workspace"], bundle["knowledge_base"]


def _workspace_response() -> dict:
  workspace, knowledge_base = _load_workspace_and_kb()
  return build_workspace_response_payload(workspace, knowledge_base)


def _workspace_response_by_id(workspace_id: str) -> dict:
  workspace, knowledge_base = _load_workspace_and_kb_by_id(workspace_id)
  return build_workspace_response_payload(workspace, knowledge_base)


@router.get("/workspace", response_model=ScriptWorkspaceResponse)
def get_script_workspace() -> dict:
  ensure_script_workspace_seeded()
  return _workspace_response()


@router.post("/workspaces", response_model=ScriptWorkspaceResponse, status_code=201)
def create_script_workspace_handler() -> dict:
  bundle = create_new_script_workspace()
  return build_workspace_response_payload(bundle["workspace"], bundle["knowledge_base"])


@router.get("/workspaces/{workspace_id}", response_model=ScriptWorkspaceResponse)
def get_script_workspace_by_id(workspace_id: str) -> dict:
  return _workspace_response_by_id(workspace_id)


@router.get("/history", response_model=ScriptHistoryResponse)
def get_script_history() -> dict:
  ensure_script_workspace_seeded()
  history: list[dict] = []
  with db_connection() as conn:
    workspaces = list_script_workspaces(conn)
    for workspace in workspaces:
      observations = workspace.get("observations") or {}
      has_activity = bool(
        (workspace.get("task") or "").strip()
        or (workspace.get("selected_source") or "").strip()
        or any(observations.get(key) for key in ("perilaku", "emosi", "situasi"))
        or workspace.get("moments")
      )
      if not has_activity:
        continue
      history.append(
        {
          "id": workspace["id"],
          "title": workspace.get("title") or "Draft script aktif",
          "task_preview": (workspace.get("task") or "").strip()[:180],
          "selected_source": (workspace.get("selected_source") or "").strip(),
          "current_step": workspace.get("current_step") or "task",
          "moment_count": len(workspace.get("moments") or []),
          "updated_at": workspace["updated_at"],
        }
      )
  history.sort(key=lambda item: item["updated_at"], reverse=True)
  return {"history": history}


def _update_script_workspace_task(workspace_id: str | None, payload: ScriptTaskUpdateRequest) -> dict:
  workspace, knowledge_base = _load_workspace_and_kb_by_id(workspace_id) if workspace_id else _load_workspace_and_kb()
  with db_connection() as conn:
    updated = update_script_workspace(
      conn,
      workspace["id"],
      {
        "task": payload.task.strip(),
        "current_step": "task",
        "active_profile_id": "",
        "selected_source": "",
        "source_options": [],
        "observations": {"perilaku": [], "emosi": [], "situasi": []},
        "moments": [],
        "observation_variant_index": 0,
        "moment_variant_index": 0,
      },
    )
    knowledge_base = get_script_knowledge_base(conn, workspace["knowledge_base_id"]) or knowledge_base
  return build_workspace_response_payload(updated, knowledge_base)


@router.patch("/workspace/task", response_model=ScriptWorkspaceResponse)
def update_script_workspace_task(payload: ScriptTaskUpdateRequest) -> dict:
  return _update_script_workspace_task(None, payload)


@router.patch("/workspaces/{workspace_id}/task", response_model=ScriptWorkspaceResponse)
def update_script_workspace_task_by_id(workspace_id: str, payload: ScriptTaskUpdateRequest) -> dict:
  return _update_script_workspace_task(workspace_id, payload)


def _generate_script_source_options(workspace_id: str | None) -> dict:
  workspace, knowledge_base = _load_workspace_and_kb_by_id(workspace_id) if workspace_id else _load_workspace_and_kb()
  task = (workspace.get("task") or "").strip()
  if not task:
    raise HTTPException(status_code=400, detail="Task wajib diisi sebelum memilih source.")

  profile_id, source_options = shortlist_sources(task, knowledge_base)
  if not source_options:
    raise HTTPException(status_code=400, detail="Source belum bisa disiapkan untuk task ini.")

  with db_connection() as conn:
    updated = update_script_workspace(
      conn,
      workspace["id"],
      {
        "current_step": "source",
        "active_profile_id": profile_id,
        "selected_source": source_options[0]["text"],
        "source_options": source_options,
        "observations": {"perilaku": [], "emosi": [], "situasi": []},
        "moments": [],
        "observation_variant_index": 0,
        "moment_variant_index": 0,
      },
    )
    knowledge_base = get_script_knowledge_base(conn, workspace["knowledge_base_id"]) or knowledge_base
  return build_workspace_response_payload(updated, knowledge_base)


@router.post("/workspace/source-options", response_model=ScriptWorkspaceResponse)
def generate_script_source_options() -> dict:
  return _generate_script_source_options(None)


@router.post("/workspaces/{workspace_id}/source-options", response_model=ScriptWorkspaceResponse)
def generate_script_source_options_by_id(workspace_id: str) -> dict:
  return _generate_script_source_options(workspace_id)


def _update_script_source(workspace_id: str | None, payload: ScriptSourceSelectionRequest) -> dict:
  workspace, knowledge_base = _load_workspace_and_kb_by_id(workspace_id) if workspace_id else _load_workspace_and_kb()
  selected_source = payload.selected_source.strip()
  if not selected_source:
    raise HTTPException(status_code=400, detail="Source tidak boleh kosong.")

  profile_id = workspace.get("active_profile_id") or detect_profile_id(workspace.get("task", ""), selected_source)
  with db_connection() as conn:
    updated = update_script_workspace(
      conn,
      workspace["id"],
      {
        "current_step": "source",
        "active_profile_id": profile_id,
        "selected_source": selected_source,
        "observations": {"perilaku": [], "emosi": [], "situasi": []},
        "moments": [],
        "observation_variant_index": 0,
        "moment_variant_index": 0,
      },
    )
    knowledge_base = get_script_knowledge_base(conn, workspace["knowledge_base_id"]) or knowledge_base
  return build_workspace_response_payload(updated, knowledge_base)


@router.patch("/workspace/source", response_model=ScriptWorkspaceResponse)
def update_script_source(payload: ScriptSourceSelectionRequest) -> dict:
  return _update_script_source(None, payload)


@router.patch("/workspaces/{workspace_id}/source", response_model=ScriptWorkspaceResponse)
def update_script_source_by_id(workspace_id: str, payload: ScriptSourceSelectionRequest) -> dict:
  return _update_script_source(workspace_id, payload)


def _generate_script_observations(workspace_id: str | None, payload: ScriptGenerationRequest) -> dict:
  workspace, knowledge_base = _load_workspace_and_kb_by_id(workspace_id) if workspace_id else _load_workspace_and_kb()
  if not (workspace.get("selected_source") or "").strip():
    raise HTTPException(status_code=400, detail="Pilih source dulu sebelum generate observasi.")

  profile_id = workspace.get("active_profile_id") or detect_profile_id(
    workspace.get("task", ""), workspace.get("selected_source", "")
  )
  current_index = int(workspace.get("observation_variant_index") or 0)
  next_index = current_index + 1 if payload.regenerate else current_index
  observations = generate_observations(knowledge_base, profile_id, next_index)

  with db_connection() as conn:
    updated = update_script_workspace(
      conn,
      workspace["id"],
      {
        "current_step": "observasi",
        "active_profile_id": profile_id,
        "observations": observations,
        "moments": [],
        "observation_variant_index": next_index,
        "moment_variant_index": 0,
      },
    )
    knowledge_base = get_script_knowledge_base(conn, workspace["knowledge_base_id"]) or knowledge_base
  return build_workspace_response_payload(updated, knowledge_base)


@router.post("/workspace/observations/generate", response_model=ScriptWorkspaceResponse)
def generate_script_observations(payload: ScriptGenerationRequest) -> dict:
  return _generate_script_observations(None, payload)


@router.post("/workspaces/{workspace_id}/observations/generate", response_model=ScriptWorkspaceResponse)
def generate_script_observations_by_id(workspace_id: str, payload: ScriptGenerationRequest) -> dict:
  return _generate_script_observations(workspace_id, payload)


def _update_script_observations(workspace_id: str | None, payload: ScriptObservationsUpdateRequest) -> dict:
  workspace, knowledge_base = _load_workspace_and_kb_by_id(workspace_id) if workspace_id else _load_workspace_and_kb()
  observations = {
    "perilaku": [item.strip() for item in payload.perilaku if item.strip()],
    "emosi": [item.strip() for item in payload.emosi if item.strip()],
    "situasi": [item.strip() for item in payload.situasi if item.strip()],
  }
  with db_connection() as conn:
    updated = update_script_workspace(
      conn,
      workspace["id"],
      {
        "current_step": "observasi",
        "observations": observations,
        "moments": [],
        "moment_variant_index": 0,
      },
    )
    knowledge_base = get_script_knowledge_base(conn, workspace["knowledge_base_id"]) or knowledge_base
  return build_workspace_response_payload(updated, knowledge_base)


@router.patch("/workspace/observations", response_model=ScriptWorkspaceResponse)
def update_script_observations(payload: ScriptObservationsUpdateRequest) -> dict:
  return _update_script_observations(None, payload)


@router.patch("/workspaces/{workspace_id}/observations", response_model=ScriptWorkspaceResponse)
def update_script_observations_by_id(workspace_id: str, payload: ScriptObservationsUpdateRequest) -> dict:
  return _update_script_observations(workspace_id, payload)


def _generate_script_moments(workspace_id: str | None, payload: ScriptGenerationRequest) -> dict:
  workspace, knowledge_base = _load_workspace_and_kb_by_id(workspace_id) if workspace_id else _load_workspace_and_kb()
  observations = workspace.get("observations") or {}
  if not any(observations.get(key) for key in ("perilaku", "emosi", "situasi")):
    raise HTTPException(status_code=400, detail="Observasi wajib ada sebelum generate momen.")

  profile_id = workspace.get("active_profile_id") or detect_profile_id(
    workspace.get("task", ""), workspace.get("selected_source", "")
  )
  current_index = int(workspace.get("moment_variant_index") or 0)
  next_index = current_index + 1 if payload.regenerate else current_index
  moments = generate_moments(knowledge_base, profile_id, next_index)

  with db_connection() as conn:
    updated = update_script_workspace(
      conn,
      workspace["id"],
      {
        "current_step": "momen",
        "moments": moments,
        "moment_variant_index": next_index,
      },
    )
    knowledge_base = get_script_knowledge_base(conn, workspace["knowledge_base_id"]) or knowledge_base
  return build_workspace_response_payload(updated, knowledge_base)


@router.post("/workspace/moments/generate", response_model=ScriptWorkspaceResponse)
def generate_script_moments(payload: ScriptGenerationRequest) -> dict:
  return _generate_script_moments(None, payload)


@router.post("/workspaces/{workspace_id}/moments/generate", response_model=ScriptWorkspaceResponse)
def generate_script_moments_by_id(workspace_id: str, payload: ScriptGenerationRequest) -> dict:
  return _generate_script_moments(workspace_id, payload)


def _update_script_moments(workspace_id: str | None, payload: ScriptMomentsUpdateRequest) -> dict:
  workspace, knowledge_base = _load_workspace_and_kb_by_id(workspace_id) if workspace_id else _load_workspace_and_kb()
  moments = [item.strip() for item in payload.moments if item.strip()]
  if not moments:
    raise HTTPException(status_code=400, detail="Minimal satu momen harus tersedia.")

  with db_connection() as conn:
    updated = update_script_workspace(
      conn,
      workspace["id"],
      {
        "current_step": payload.current_step or "momen",
        "moments": moments,
      },
    )
    knowledge_base = get_script_knowledge_base(conn, workspace["knowledge_base_id"]) or knowledge_base
  return build_workspace_response_payload(updated, knowledge_base)


@router.patch("/workspace/moments", response_model=ScriptWorkspaceResponse)
def update_script_moments(payload: ScriptMomentsUpdateRequest) -> dict:
  return _update_script_moments(None, payload)


@router.patch("/workspaces/{workspace_id}/moments", response_model=ScriptWorkspaceResponse)
def update_script_moments_by_id(workspace_id: str, payload: ScriptMomentsUpdateRequest) -> dict:
  return _update_script_moments(workspace_id, payload)


def _reset_script_workspace(workspace_id: str | None) -> dict:
  workspace, knowledge_base = _load_workspace_and_kb_by_id(workspace_id) if workspace_id else _load_workspace_and_kb()
  with db_connection() as conn:
    updated = update_script_workspace(
      conn,
      workspace["id"],
      {
        "current_step": "task",
        "active_profile_id": "",
        "task": "",
        "selected_source": "",
        "source_options": [],
        "observations": {"perilaku": [], "emosi": [], "situasi": []},
        "moments": [],
        "observation_variant_index": 0,
        "moment_variant_index": 0,
      },
    )
    knowledge_base = get_script_knowledge_base(conn, workspace["knowledge_base_id"]) or knowledge_base
  return build_workspace_response_payload(updated, knowledge_base)


@router.post("/workspace/reset", response_model=ScriptWorkspaceResponse)
def reset_script_workspace() -> dict:
  return _reset_script_workspace(None)


@router.post("/workspaces/{workspace_id}/reset", response_model=ScriptWorkspaceResponse)
def reset_script_workspace_by_id(workspace_id: str) -> dict:
  return _reset_script_workspace(workspace_id)
