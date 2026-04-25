from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from app.prompting.contracts import ActionRequest, PromptBuildResult
from app.prompting.modules import PROMPT_MODULES
from app.prompting.specs import get_action_specs
from app.prompting.validators import validate_action_request, validate_prompt_build_result


class PromptBuilder:
  layer_order = ["role", "task", "policy", "context", "output"]

  def build(self, action_request: ActionRequest) -> PromptBuildResult:
    action_specs = get_action_specs()
    action_spec = action_specs.get(action_request.action_id)
    if not action_spec:
      raise ValueError(f"Unknown action id: {action_request.action_id}")

    request_validation = validate_action_request(action_request, action_spec)
    if not request_validation.is_valid:
      raise ValueError("; ".join(request_validation.errors))

    modules = [PROMPT_MODULES[name] for name in action_spec.module_names]
    layered_content = self._build_layered_content(action_request.action_id, action_request.input)
    module_versions = {module.name: module.version for module in modules}
    assembled_prompt = self._assemble_prompt(modules, layered_content)

    debug_metadata = self._build_debug_metadata(action_request, action_spec, module_versions)
    prompt_build = PromptBuildResult(
      action_id=action_spec.action_id,
      system_instructions=action_spec.system_prompt,
      runtime_context=layered_content["context"],
      assembled_prompt=assembled_prompt,
      prompt_version=action_spec.version,
      module_versions=module_versions,
      debug_metadata=debug_metadata,
      binary_parts=tuple(action_request.input.get("embed_images", ())),
      config_metadata={
        "output_mode": action_spec.output_mode,
        "model_name": action_request.metadata.get("model_name", ""),
        "aspect_ratio": action_request.input.get("aspect_ratio", "9:16"),
      },
    )

    build_validation = validate_prompt_build_result(prompt_build)
    if not build_validation.is_valid:
      raise ValueError("; ".join(build_validation.errors))

    return prompt_build

  def _assemble_prompt(self, modules: list[Any], layered_content: dict[str, str]) -> str:
    sections: list[str] = []
    for layer_name in self.layer_order:
      module_content = "\n".join(
        module.content
        for module in modules
        if module.layer == layer_name and module.content.strip()
      )
      runtime_content = layered_content.get(layer_name, "").strip()
      if not module_content and not runtime_content:
        continue
      parts = [part for part in (module_content, runtime_content) if part]
      sections.append("\n".join(parts))
    return "\n\n".join(sections)

  def _build_layered_content(self, action_id: str, payload: dict[str, Any]) -> dict[str, Any]:
    if action_id == "refine_slide_brief":
      notes = str(payload.get("notes") or "").strip()
      embed_assets = payload.get("embed_assets") or []
      aspect_ratio = str(payload.get("aspect_ratio") or "9:16").strip() or "9:16"
      embed_lines = []
      for asset in embed_assets:
        label = str(asset.get("label") or "").strip() or "Embed"
        context = str(asset.get("context") or "").strip()
        if context:
          embed_lines.append(f"- {label}: {context}")
        else:
          embed_lines.append(f"- {label}: use for the matching brand/term in the slide text.")

      notes_hint = (
        f"User notes (guidance only, do not include as visible text): {notes}"
        if notes
        else "User notes: none."
      )
      embed_hint = (
        "Embed images provided:\n"
        + "\n".join(embed_lines)
        + "\nUse each embed for its matching label/brand in the slide text and integrate it contextually."
        if embed_assets
        else "Embed images: none. Add clean, simple supportive visuals or infographics that match the layout."
      )
      slide_text = str(payload.get("slide_text") or "").strip()
      return {
        "role": "",
        "task": f"Create a production brief for a slide image with aspect ratio {aspect_ratio}.",
        "policy": "",
        "context": (
          f"Canvas aspect ratio: {aspect_ratio}\n\n"
          "Slide text:\n"
          f"{slide_text}\n\n"
          f"{notes_hint}\n"
          f"{embed_hint}"
        ),
        "output": "",
      }

    production_brief = str(payload.get("production_brief") or "").strip()
    slide_text = str(payload.get("slide_text") or "").strip()
    embed_images = payload.get("embed_images") or []
    aspect_ratio = str(payload.get("aspect_ratio") or "9:16").strip() or "9:16"
    embed_hint = (
      f"Reference images attached: {len(embed_images)}."
      if embed_images
      else "Reference images attached: none."
    )
    return {
      "role": "",
      "task": "",
      "policy": "",
      "context": (
        f"Canvas aspect ratio: {aspect_ratio}\n\n"
        "Production brief:\n"
        f"{production_brief}\n\n"
        "Visible slide text to render exactly:\n"
        f"{slide_text}\n\n"
        f"{embed_hint}"
      ),
      "output": "",
    }

  def _build_debug_metadata(
    self,
    action_request: ActionRequest,
    action_spec: Any,
    module_versions: dict[str, str],
  ) -> dict[str, Any]:
    embed_assets = action_request.input.get("embed_assets") or []
    embed_images = action_request.input.get("embed_images") or []
    notes = str(action_request.input.get("notes") or "").strip()
    slide_text = str(action_request.input.get("slide_text") or "")
    aspect_ratio = str(action_request.input.get("aspect_ratio") or "9:16").strip() or "9:16"
    return {
      "action_id": action_spec.action_id,
      "layers": list(self.layer_order),
      "module_versions": module_versions,
      "model_name": action_request.metadata.get("model_name", ""),
      "has_notes": bool(notes),
      "embed_count": len(embed_assets) or len(embed_images),
      "grounding_enabled": bool(action_request.input.get("use_grounding", False)),
      "slide_text_length": len(slide_text),
      "aspect_ratio": aspect_ratio,
      "context_truncated": False,
      "timestamp": datetime.now(timezone.utc).isoformat(),
    }


prompt_builder = PromptBuilder()
