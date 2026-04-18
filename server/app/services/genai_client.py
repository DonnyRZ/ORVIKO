from __future__ import annotations

from io import BytesIO
import logging
from typing import List, Sequence

from google import genai
from google.genai import types
from PIL import Image, ImageStat

from app.core.config import get_settings
from app.prompting import prompt_builder
from app.prompting.contracts import ActionRequest
from app.prompting.validators import validate_image_output, validate_refiner_output


logger = logging.getLogger(__name__)
_DARK_MOOD_TERMS = (
  "dark",
  "moody",
  "gloomy",
  "dramatic",
  "cinematic",
  "noir",
  "night",
  "shadow",
  "low-key",
  "low key",
  "mysterious",
  "gritty",
)
_BRIGHT_MOOD_TERMS = (
  "bright",
  "airy",
  "clean",
  "fresh",
  "luminous",
  "light",
  "sunny",
  "open",
)
_TOO_DARK_BRIGHTNESS_THRESHOLD = 0.36


def _infer_requested_mood(*values: str | None) -> str:
  combined = " ".join(value.strip().lower() for value in values if value and value.strip())
  if any(term in combined for term in _DARK_MOOD_TERMS):
    return "dark"
  if any(term in combined for term in _BRIGHT_MOOD_TERMS):
    return "light"
  return "balanced-light"


def _calculate_image_brightness(image_bytes: bytes) -> float:
  image = Image.open(BytesIO(image_bytes)).convert("L")
  return float(ImageStat.Stat(image).mean[0]) / 255.0


def _bucket_brightness(brightness: float) -> str:
  if brightness < _TOO_DARK_BRIGHTNESS_THRESHOLD:
    return "too_dark"
  if brightness < 0.5:
    return "balanced"
  return "bright"


def _should_retry_dark_result(requested_mood: str, brightness: float) -> bool:
  return requested_mood != "dark" and brightness < _TOO_DARK_BRIGHTNESS_THRESHOLD


def _build_brightness_repair_instruction(requested_mood: str) -> str:
  if requested_mood == "light":
    target = "bright, airy, luminous, and clean"
  else:
    target = "balanced-light, open, readable, and non-gloomy"
  return (
    " Repair instruction: keep the composition strong but shift the palette and lighting toward a "
    f"{target} result. Do not use a dark, moody, cinematic, or low-key treatment unless the provided text explicitly requires it."
  )


class GenAIClient:
  def __init__(self) -> None:
    settings = get_settings()
    self.settings = settings
    self.prompt_client = genai.Client(api_key=settings.genai_api_key)
    self.image_client = genai.Client(api_key=settings.image_ai_key)
    self.prompt_model = settings.genai_model
    self.image_model = settings.image_model
    self.refiner_system_prompt = settings.refiner_system_prompt or settings.system_prompt
    self.image_system_prompt = settings.image_system_prompt or settings.system_prompt
    self.image_aspect_ratio = settings.image_aspect_ratio
    self.image_size = settings.image_size
    self.allow_google_search = settings.allow_google_search

  def refine_prompt(
    self,
    slide_text: str,
    notes: str | None,
    embed_assets: Sequence[dict[str, str]],
  ) -> str:
    action_request = ActionRequest(
      action_id="refine_slide_brief",
      input={
        "slide_text": slide_text,
        "notes": notes,
        "embed_assets": list(embed_assets),
      },
      metadata={"model_name": self.prompt_model},
    )
    prompt_build = prompt_builder.build(action_request)
    logger.info(
      "Prompt build ready",
      extra={"prompting": prompt_build.debug_metadata},
    )
    response = self.prompt_client.models.generate_content(
      model=self.prompt_model,
      contents=[
        types.Content(
          role="user",
          parts=[types.Part.from_text(text=prompt_build.assembled_prompt)],
        )
      ],
      config=types.GenerateContentConfig(
        systemInstruction=prompt_build.system_instructions,
        response_modalities=["TEXT"],
      ),
    )
    refined = (response.text or "").strip()
    validation = validate_refiner_output(refined)
    logger.info(
      "Refiner output validated",
      extra={
        "prompting": {
          "action_id": prompt_build.action_id,
          "is_valid": validation.is_valid,
          "errors": list(validation.errors),
        }
      },
    )
    return refined or prompt_build.assembled_prompt

  def generate_images(
    self,
    slide_text: str,
    production_brief: str,
    embed_images: Sequence[tuple[str, bytes]],
    count: int,
    use_grounding: bool = False,
    notes: str | None = None,
  ) -> List[bytes]:
    requested_mood = _infer_requested_mood(notes, production_brief, slide_text)
    action_request = ActionRequest(
      action_id="generate_slide_image",
      input={
        "slide_text": slide_text,
        "production_brief": production_brief,
        "embed_images": list(embed_images),
        "use_grounding": use_grounding,
        "notes": notes,
      },
      metadata={"model_name": self.image_model},
    )
    prompt_build = prompt_builder.build(action_request)
    base_prompt_text = prompt_build.assembled_prompt
    logger.info(
      "Prompt build ready",
      extra={
        "prompting": {
          **prompt_build.debug_metadata,
          "requested_mood": requested_mood,
        }
      },
    )
    embed_parts = [
      types.Part.from_bytes(data=payload, mime_type=mime_type or "image/png")
      for mime_type, payload in prompt_build.binary_parts
    ]
    response_modalities = ["IMAGE"]
    if use_grounding:
      if not self.allow_google_search:
        raise RuntimeError("Google Search grounding is disabled. Set ALLOW_GOOGLE_SEARCH=true to enable.")
      response_modalities = ["TEXT", "IMAGE"]

    image_config = None
    image_config_factory = getattr(types, "ImageConfig", None)
    if image_config_factory is not None:
      image_config = image_config_factory(aspect_ratio=self.image_aspect_ratio)
      if self.image_size and "pro-image-preview" in self.image_model:
        image_config.image_size = self.image_size

    config_kwargs = {
      "systemInstruction": prompt_build.system_instructions,
      "response_modalities": response_modalities,
    }
    if image_config is not None:
      config_kwargs["image_config"] = image_config
    if use_grounding:
      config_kwargs["tools"] = [{"google_search": {}}]

    results = []
    for _ in range(count):
      retry_used = False
      prompt_text = base_prompt_text
      image_bytes = None
      brightness = 0.0
      brightness_bucket = "unknown"

      for attempt in range(2):
        response = self.image_client.models.generate_content(
          model=self.image_model,
          contents=[
            types.Content(
              role="user",
              parts=[types.Part.from_text(text=prompt_text), *embed_parts],
            )
          ],
          config=types.GenerateContentConfig(**config_kwargs),
        )

        image_bytes = None
        for candidate in response.candidates or []:
          for part in candidate.content.parts:
            if hasattr(part, "inline_data") and part.inline_data:
              image_bytes = part.inline_data.data
              break
          if image_bytes:
            break

        validation = validate_image_output(image_bytes)
        if not validation.is_valid:
          logger.info(
            "Image output validated",
            extra={
              "prompting": {
                "action_id": prompt_build.action_id,
                "is_valid": validation.is_valid,
                "errors": list(validation.errors),
                "requested_mood": requested_mood,
                "dark_retry_used": retry_used,
              }
            },
          )
          raise RuntimeError("Image generation returned no data.")

        brightness = _calculate_image_brightness(image_bytes)
        brightness_bucket = _bucket_brightness(brightness)
        should_retry = attempt == 0 and _should_retry_dark_result(requested_mood, brightness)
        logger.info(
          "Image output validated",
          extra={
            "prompting": {
              "action_id": prompt_build.action_id,
              "is_valid": validation.is_valid,
              "errors": list(validation.errors),
              "requested_mood": requested_mood,
              "detected_brightness": round(brightness, 4),
              "final_brightness_bucket": brightness_bucket,
              "dark_retry_used": retry_used,
              "retry_triggered": should_retry,
            }
          },
        )
        if not should_retry:
          break

        retry_used = True
        prompt_text = base_prompt_text + _build_brightness_repair_instruction(requested_mood)

      results.append(image_bytes)

    return results


genai_client = GenAIClient()
