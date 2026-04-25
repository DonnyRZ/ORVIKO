from types import SimpleNamespace

from app.services import genai_client as genai_module


class _FakePart:
  def __init__(self, *, text: str | None = None, data: bytes | None = None, mime_type: str | None = None) -> None:
    self.text = text
    self.inline_data = SimpleNamespace(data=data) if data is not None else None
    self.mime_type = mime_type

  @classmethod
  def from_text(cls, text: str) -> "_FakePart":
    return cls(text=text)

  @classmethod
  def from_bytes(cls, data: bytes, mime_type: str) -> "_FakePart":
    return cls(data=data, mime_type=mime_type)


class _FakeContent:
  def __init__(self, role: str, parts: list[_FakePart]) -> None:
    self.role = role
    self.parts = parts


class _FakeGenerateContentConfig:
  def __init__(self, **kwargs) -> None:
    self.kwargs = kwargs


class _FakeModels:
  def __init__(self, responses: list[object]) -> None:
    self._responses = responses
    self.calls: list[dict] = []

  def generate_content(self, **kwargs):
    self.calls.append(kwargs)
    return self._responses.pop(0)


class _FakeClient:
  def __init__(self, responses: list[object]) -> None:
    self.models = _FakeModels(responses)


def _build_client() -> genai_module.GenAIClient:
  client = genai_module.GenAIClient.__new__(genai_module.GenAIClient)
  client.settings = SimpleNamespace()
  client.prompt_model = "gemini-text-test"
  client.image_model = "gemini-image-test"
  client.refiner_system_prompt = "unused"
  client.image_system_prompt = "unused"
  client.image_aspect_ratio = "9:16"
  client.image_size = "2K"
  client.allow_google_search = True
  return client


def test_refine_prompt_uses_built_prompt_and_falls_back_when_empty(monkeypatch) -> None:
  fake_types = SimpleNamespace(
    Part=_FakePart,
    Content=_FakeContent,
    GenerateContentConfig=_FakeGenerateContentConfig,
    ImageConfig=None,
  )
  monkeypatch.setattr(genai_module, "types", fake_types)

  client = _build_client()
  client.prompt_client = _FakeClient([SimpleNamespace(text="")])
  client.image_client = _FakeClient([])

  result = client.refine_prompt("Slide text", "", [])

  call = client.prompt_client.models.calls[0]
  prompt_text = call["contents"][0].parts[0].text
  assert result == prompt_text
  assert "Slide text:\nSlide text" in prompt_text


def test_generate_images_returns_first_valid_inline_data(monkeypatch) -> None:
  fake_types = SimpleNamespace(
    Part=_FakePart,
    Content=_FakeContent,
    GenerateContentConfig=_FakeGenerateContentConfig,
    ImageConfig=None,
  )
  monkeypatch.setattr(genai_module, "types", fake_types)
  monkeypatch.setattr(genai_module, "_calculate_image_brightness", lambda image_bytes: 0.55)

  candidate = SimpleNamespace(content=SimpleNamespace(parts=[_FakePart.from_bytes(b"image", "image/png")]))
  response = SimpleNamespace(candidates=[candidate])

  client = _build_client()
  client.prompt_client = _FakeClient([])
  client.image_client = _FakeClient([response])

  result = client.generate_images(
    slide_text="Visible",
    production_brief="Brief",
    embed_images=[("image/png", b"embed")],
    count=1,
    use_grounding=True,
    notes="",
  )

  call = client.image_client.models.calls[0]
  prompt_text = call["contents"][0].parts[0].text
  assert result == [b"image"]
  assert "Production brief:\nBrief" in prompt_text
  assert call["config"].kwargs["tools"] == [{"google_search": {}}]


def test_generate_images_raises_when_no_inline_data(monkeypatch) -> None:
  fake_types = SimpleNamespace(
    Part=_FakePart,
    Content=_FakeContent,
    GenerateContentConfig=_FakeGenerateContentConfig,
    ImageConfig=None,
  )
  monkeypatch.setattr(genai_module, "types", fake_types)
  monkeypatch.setattr(genai_module, "_calculate_image_brightness", lambda image_bytes: 0.55)

  candidate = SimpleNamespace(content=SimpleNamespace(parts=[_FakePart.from_text("no image")]))
  response = SimpleNamespace(candidates=[candidate])

  client = _build_client()
  client.prompt_client = _FakeClient([])
  client.image_client = _FakeClient([response])

  try:
    client.generate_images(
      slide_text="Visible",
      production_brief="Brief",
      embed_images=[],
      count=1,
      notes="",
    )
  except RuntimeError as exc:
    assert str(exc) == "Image generation returned no data."
  else:
    raise AssertionError("Expected RuntimeError when no image bytes are returned.")


def test_generate_images_retries_when_first_result_is_too_dark(monkeypatch) -> None:
  fake_types = SimpleNamespace(
    Part=_FakePart,
    Content=_FakeContent,
    GenerateContentConfig=_FakeGenerateContentConfig,
    ImageConfig=None,
  )
  monkeypatch.setattr(genai_module, "types", fake_types)

  brightness_values = iter([0.2, 0.58])
  monkeypatch.setattr(genai_module, "_calculate_image_brightness", lambda image_bytes: next(brightness_values))

  dark_candidate = SimpleNamespace(content=SimpleNamespace(parts=[_FakePart.from_bytes(b"dark-image", "image/png")]))
  bright_candidate = SimpleNamespace(content=SimpleNamespace(parts=[_FakePart.from_bytes(b"bright-image", "image/png")]))
  responses = [SimpleNamespace(candidates=[dark_candidate]), SimpleNamespace(candidates=[bright_candidate])]

  client = _build_client()
  client.prompt_client = _FakeClient([])
  client.image_client = _FakeClient(responses)

  result = client.generate_images(
    slide_text="Helpful headline",
    production_brief="Visual Style: balanced-light and readable.",
    embed_images=[],
    count=1,
    notes="",
  )

  assert result == [b"bright-image"]
  assert len(client.image_client.models.calls) == 2
  retry_prompt = client.image_client.models.calls[1]["contents"][0].parts[0].text
  assert "Repair instruction:" in retry_prompt


def test_generate_images_does_not_retry_for_dark_requested_mood(monkeypatch) -> None:
  fake_types = SimpleNamespace(
    Part=_FakePart,
    Content=_FakeContent,
    GenerateContentConfig=_FakeGenerateContentConfig,
    ImageConfig=None,
  )
  monkeypatch.setattr(genai_module, "types", fake_types)
  monkeypatch.setattr(genai_module, "_calculate_image_brightness", lambda image_bytes: 0.2)

  candidate = SimpleNamespace(content=SimpleNamespace(parts=[_FakePart.from_bytes(b"dark-image", "image/png")]))
  response = SimpleNamespace(candidates=[candidate])

  client = _build_client()
  client.prompt_client = _FakeClient([])
  client.image_client = _FakeClient([response])

  result = client.generate_images(
    slide_text="Serious night concept",
    production_brief="Visual Style: dark and dramatic.",
    embed_images=[],
    count=1,
    notes="dark dramatic mood",
  )

  assert result == [b"dark-image"]
  assert len(client.image_client.models.calls) == 1
