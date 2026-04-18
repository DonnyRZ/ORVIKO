from __future__ import annotations

from app.prompting.contracts import ActionRequest, ActionSpec, PromptBuildResult, ValidationResult


def validate_action_request(action_request: ActionRequest, action_spec: ActionSpec) -> ValidationResult:
  errors: list[str] = []
  if action_request.action_id != action_spec.action_id:
    errors.append("Action request id does not match action spec.")

  for field_name in action_spec.required_inputs:
    if field_name not in action_request.input:
      errors.append(f"Missing required input: {field_name}.")
      continue
    value = action_request.input[field_name]
    if field_name == "slide_text" and not str(value or "").strip():
      errors.append("slide_text must not be empty.")
    if field_name == "production_brief" and not str(value or "").strip():
      errors.append("production_brief must not be empty.")

  return ValidationResult(is_valid=not errors, errors=tuple(errors))


def validate_prompt_build_result(prompt_build: PromptBuildResult) -> ValidationResult:
  errors: list[str] = []
  if not prompt_build.action_id:
    errors.append("Prompt build is missing action id.")
  if not prompt_build.system_instructions.strip():
    errors.append("Prompt build is missing system instructions.")
  if not prompt_build.assembled_prompt.strip():
    errors.append("Prompt build is missing assembled prompt.")
  if not prompt_build.prompt_version:
    errors.append("Prompt build is missing prompt version.")
  if not prompt_build.module_versions:
    errors.append("Prompt build is missing module versions.")

  layers = prompt_build.debug_metadata.get("layers")
  if not isinstance(layers, list) or layers != ["role", "task", "policy", "context", "output"]:
    errors.append("Prompt layers are incomplete or out of order.")

  return ValidationResult(is_valid=not errors, errors=tuple(errors))


def validate_refiner_output(text: str) -> ValidationResult:
  errors = () if text.strip() else ("Refiner output is empty.",)
  return ValidationResult(is_valid=not errors, errors=errors)


def validate_image_output(image_bytes: bytes | None) -> ValidationResult:
  errors = () if image_bytes else ("Image generation returned no data.",)
  return ValidationResult(is_valid=not errors, errors=errors)
