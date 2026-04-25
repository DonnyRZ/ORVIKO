from typing import Literal, Optional

from pydantic import BaseModel, Field

ScriptStep = Literal["task", "source", "observasi", "momen", "result"]


class ScriptSourceOption(BaseModel):
  title: str
  text: str


class ScriptObservations(BaseModel):
  perilaku: list[str] = Field(default_factory=list)
  emosi: list[str] = Field(default_factory=list)
  situasi: list[str] = Field(default_factory=list)


class ScriptKnowledgeBaseSummary(BaseModel):
  id: str
  title: str
  creator: str
  audience: str
  source_patterns: list[str] = Field(default_factory=list)
  moment_patterns: list[str] = Field(default_factory=list)
  sample_tasks: list[str] = Field(default_factory=list)


class ScriptWorkspace(BaseModel):
  id: str
  title: str
  knowledge_base_id: str
  current_step: ScriptStep
  active_profile_id: str = ""
  task: str = ""
  selected_source: str = ""
  source_options: list[ScriptSourceOption] = Field(default_factory=list)
  observations: ScriptObservations = Field(default_factory=ScriptObservations)
  moments: list[str] = Field(default_factory=list)
  observation_variant_index: int = 0
  moment_variant_index: int = 0
  created_at: str
  updated_at: str


class ScriptWorkspaceResponse(BaseModel):
  workspace: ScriptWorkspace
  knowledge_base: ScriptKnowledgeBaseSummary


class ScriptHistoryItem(BaseModel):
  id: str
  title: str
  task_preview: str
  selected_source: str = ""
  current_step: ScriptStep
  moment_count: int
  updated_at: str


class ScriptHistoryResponse(BaseModel):
  history: list[ScriptHistoryItem] = Field(default_factory=list)


class ScriptTaskUpdateRequest(BaseModel):
  task: str = Field("", max_length=3000)


class ScriptSourceSelectionRequest(BaseModel):
  selected_source: str = Field("", max_length=1000)


class ScriptGenerationRequest(BaseModel):
  regenerate: bool = Field(False)


class ScriptObservationsUpdateRequest(BaseModel):
  perilaku: list[str] = Field(default_factory=list)
  emosi: list[str] = Field(default_factory=list)
  situasi: list[str] = Field(default_factory=list)


class ScriptMomentsUpdateRequest(BaseModel):
  moments: list[str] = Field(default_factory=list)
  current_step: Optional[ScriptStep] = None
