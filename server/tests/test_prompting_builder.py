from app.prompting.builder import prompt_builder
from app.prompting.contracts import ActionRequest


def test_refine_slide_brief_builder_creates_layered_prompt() -> None:
  result = prompt_builder.build(
    ActionRequest(
      action_id="refine_slide_brief",
      input={
        "slide_text": "Hello world",
        "notes": "",
        "embed_assets": [],
      },
      metadata={"model_name": "gemini-test"},
    )
  )

  assert result.action_id == "refine_slide_brief"
  assert result.debug_metadata["layers"] == ["role", "task", "policy", "context", "output"]
  assert result.debug_metadata["has_notes"] is False
  assert result.debug_metadata["embed_count"] == 0
  assert result.prompt_version == "1.0"
  assert "You are a visual slide design strategist." in result.assembled_prompt
  assert "Create a production brief for a 9:16 slide image." in result.assembled_prompt
  assert "Slide text:\nHello world" in result.assembled_prompt
  assert "User notes: none." in result.assembled_prompt
  assert "Embed images: none." in result.assembled_prompt
  assert "High-quality visuals may be bright, airy, fresh, luminous, colorful, or clean" in result.assembled_prompt
  assert "prefer a balanced-light, readable, non-gloomy direction" in result.assembled_prompt
  assert "Composition, Text Treatment, Visual Style, Background, Embed Usage, and Constraints" in result.assembled_prompt


def test_generate_slide_image_builder_preserves_context_and_binary_parts() -> None:
  result = prompt_builder.build(
    ActionRequest(
      action_id="generate_slide_image",
      input={
        "slide_text": "Visible headline",
        "production_brief": "Composition: strong hierarchy",
        "embed_images": [("image/png", b"123")],
        "use_grounding": True,
      },
      metadata={"model_name": "gemini-image-test"},
    )
  )

  assert result.action_id == "generate_slide_image"
  assert result.debug_metadata["grounding_enabled"] is True
  assert result.debug_metadata["embed_count"] == 1
  assert result.binary_parts == (("image/png", b"123"),)
  assert "You are generating a clean vertical slide image." in result.assembled_prompt
  assert "Production brief:\nComposition: strong hierarchy" in result.assembled_prompt
  assert "Visible slide text to render exactly:\nVisible headline" in result.assembled_prompt
  assert "Strong contrast does not mean low-key lighting or a dark palette by default." in result.assembled_prompt
