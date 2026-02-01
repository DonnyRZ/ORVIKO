from __future__ import annotations

from typing import List, Sequence

from google import genai
from google.genai import types

from app.core.config import get_settings


def _build_user_prompt(
  slide_text: str,
  design: str | None,
  embed_assets: Sequence[dict[str, str]],
) -> str:
  embed_lines = []
  for asset in embed_assets:
    label = (asset.get("label") or "").strip() or "Embed"
    context = (asset.get("context") or "").strip()
    if context:
      embed_lines.append(f"- {label}: {context}")
    else:
      embed_lines.append(f"- {label}: use for the matching brand/term in the slide text.")
  design_line = design.strip() if design else ""
  design_hint = (
    f"Design input (must be respected): {design_line}"
    if design_line
    else "Design input: not provided. Choose a layout based on the text context."
  )
  embed_hint = (
    "Embed images provided:\n"
    + "\n".join(embed_lines)
    + "\nUse each embed for its matching label/brand in the slide text and integrate it contextually."
    if embed_assets
    else "Embed images: none. Add clean, simple supportive visuals or infographics that match the design."
  )
  return (
    "Create a TikTok slide image in 9:16 (1080x1920).\n"
    "The slide text is the source of truth and must be used exactly and fully (no extra text).\n"
    f"Slide text:\n{slide_text}\n\n"
    f"{design_hint}\n"
    f"{embed_hint}\n"
    "Rules: adjust text size/placement to fit the context, keep the background minimal noise, "
    "and keep important content centered within a safe vertical area."
  )


class GenAIClient:
  def __init__(self) -> None:
    settings = get_settings()
    self.settings = settings
    self.prompt_client = genai.Client(api_key=settings.genai_api_key)
    self.image_client = genai.Client(api_key=settings.image_ai_key)
    self.prompt_model = settings.genai_model
    self.image_model = settings.image_model
    self.system_prompt = settings.system_prompt
    self.image_aspect_ratio = settings.image_aspect_ratio
    self.image_size = settings.image_size
    self.allow_google_search = settings.allow_google_search

  def refine_prompt(
    self,
    slide_text: str,
    design: str | None,
    embed_assets: Sequence[dict[str, str]],
  ) -> str:
    base_prompt = _build_user_prompt(slide_text, design, embed_assets)
    response = self.prompt_client.models.generate_content(
      model=self.prompt_model,
      contents=[
        types.Content(
          role="user",
          parts=[types.Part.from_text(text=base_prompt)],
        )
      ],
      config=types.GenerateContentConfig(
        systemInstruction=self.system_prompt,
        response_modalities=["TEXT"],
      ),
    )
    refined = (response.text or "").strip()
    return refined or base_prompt

  def generate_images(
    self,
    prompt: str,
    embed_images: Sequence[tuple[str, bytes]],
    count: int,
    use_grounding: bool = False,
  ) -> List[bytes]:
    embed_parts = [
      types.Part.from_bytes(data=payload, mime_type=mime_type or "image/png")
      for mime_type, payload in embed_images
    ]
    response_modalities = ["IMAGE"]
    if use_grounding:
      if not self.allow_google_search:
        raise RuntimeError("Google Search grounding is disabled. Set ALLOW_GOOGLE_SEARCH=true to enable.")
      response_modalities = ["TEXT", "IMAGE"]

    image_config = None
    if hasattr(types, "ImageConfig"):
      image_config = types.ImageConfig(aspect_ratio=self.image_aspect_ratio)
      if self.image_size and "pro-image-preview" in self.image_model:
        image_config.image_size = self.image_size

    config_kwargs = {
      "systemInstruction": self.system_prompt,
      "response_modalities": response_modalities,
    }
    if image_config is not None:
      config_kwargs["image_config"] = image_config
    if use_grounding:
      config_kwargs["tools"] = [{"google_search": {}}]

    results = []
    for _ in range(count):
      response = self.image_client.models.generate_content(
        model=self.image_model,
        contents=[
          types.Content(
            role="user",
            parts=[types.Part.from_text(text=prompt), *embed_parts],
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

      if not image_bytes:
        raise RuntimeError("Image generation returned no data.")

      results.append(image_bytes)

    return results


genai_client = GenAIClient()
