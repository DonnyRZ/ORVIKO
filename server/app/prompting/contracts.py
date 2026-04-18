from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal


PromptLayer = Literal["role", "task", "policy", "context", "output"]


@dataclass(frozen=True)
class PromptModule:
  name: str
  layer: PromptLayer
  content: str
  version: str = "1.0"


@dataclass(frozen=True)
class ActionSpec:
  action_id: str
  goal: str
  system_prompt: str
  output_mode: Literal["text", "image"]
  module_names: tuple[str, ...]
  required_inputs: tuple[str, ...]
  version: str = "1.0"


@dataclass(frozen=True)
class ActionRequest:
  action_id: str
  input: dict[str, Any]
  metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class PromptBuildResult:
  action_id: str
  system_instructions: str
  runtime_context: dict[str, Any]
  assembled_prompt: str
  prompt_version: str
  module_versions: dict[str, str]
  debug_metadata: dict[str, Any]
  binary_parts: tuple[Any, ...] = ()
  config_metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ValidationResult:
  is_valid: bool
  errors: tuple[str, ...] = ()
  warnings: tuple[str, ...] = ()
