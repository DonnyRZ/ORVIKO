from __future__ import annotations

from app.core.config import get_settings
from app.prompting.contracts import ActionSpec


def get_action_specs() -> dict[str, ActionSpec]:
  settings = get_settings()
  return {
    "refine_slide_brief": ActionSpec(
      action_id="refine_slide_brief",
      goal="Turn slide text, notes, and embed hints into a concise production brief.",
      system_prompt=settings.refiner_system_prompt or settings.system_prompt,
      output_mode="text",
      module_names=("refiner_role", "refiner_task", "refiner_policy", "refiner_output"),
      required_inputs=("slide_text", "embed_assets"),
    ),
    "generate_slide_image": ActionSpec(
      action_id="generate_slide_image",
      goal="Generate a 9:16 slide image from the production brief, exact slide text, and embed images.",
      system_prompt=settings.image_system_prompt or settings.system_prompt,
      output_mode="image",
      module_names=("image_role", "image_task", "image_policy", "image_output"),
      required_inputs=("slide_text", "production_brief", "embed_images"),
    ),
  }
