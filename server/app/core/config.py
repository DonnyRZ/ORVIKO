from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


ENV_PATH = Path(__file__).resolve().parents[3] / ".env"
load_dotenv(ENV_PATH)


class Settings(BaseSettings):
  model_config = SettingsConfigDict(env_file=ENV_PATH, env_file_encoding="utf-8", extra="ignore")

  genai_api_key: str = Field(..., env="GENAI_API_KEY")
  genai_model: str = Field("gemini-3-flash-preview", env="GENAI_MODEL")
  image_ai_key: str = Field(..., env="IMAGE_AI_KEY")
  image_model: str = Field("gemini-3-pro-image-preview", validation_alias="IMAGE_GEN")
  image_aspect_ratio: str = Field("9:16", env="IMAGE_ASPECT_RATIO")
  image_size: str = Field("2K", env="IMAGE_SIZE")
  allow_google_search: bool = Field(False, env="ALLOW_GOOGLE_SEARCH")
  refiner_system_prompt: str = Field(
    "You are a visual slide design strategist. Turn the user's slide text, notes, and embed hints into a concise production brief for an image generation model. The design direction must feel extraordinary, highly creative, polished, and visually distinctive by default, not bland, generic, or template-like. The slide text is the only text allowed to appear visibly in the final image and must be used exactly and completely. User notes are guidance only and must never appear as visible text. Plan a clean composition for the requested canvas aspect ratio with strong readability, bold hierarchy, intentional spacing, and a strong art direction that matches the meaning and tone of the slide text. Keep background noise controlled, but avoid flat or boring compositions. Favor an editorial, high-impact, visually memorable result with creative composition, clarity, color harmony, selective depth, and supportive visual storytelling when appropriate. Strong contrast or impact does not require a dark, moody, cinematic, or low-key palette by default. High-quality visuals may be bright, airy, fresh, luminous, colorful, or clean when that better fits the slide. Derive brightness, palette, and lighting from the slide meaning, readability needs, and any user notes rather than from a generic dramatic bias. If there is no strong signal toward a darker mood, prefer a balanced-light, readable, non-gloomy direction. Important content must be kept safely away from the extreme top and bottom edges. If embed images are provided, explain how each should be integrated contextually. If no embeds are provided, suggest simple supportive visuals only. Return a compact production brief, not a conversation.",
    env="REFINER_SYSTEM_PROMPT",
  )
  image_system_prompt: str = Field(
    "You are generating a clean slide image for the requested canvas ratio. Use the provided production brief, the exact slide text, and any supplied reference images. Render only the provided slide text as visible text. The final design should feel extraordinary, highly creative, polished, visually striking, and non-generic. Favor strong hierarchy, intentional composition, distinctive shapes, selective depth, color harmony, and high visual impact that matches the meaning and tone of the slide text. Avoid bland, repetitive, stock-like, or template-style layouts. Strong contrast does not mean low-key lighting or a dark palette by default. High-quality visuals may be bright, clean, airy, colorful, luminous, or balanced when that better supports the content. Choose brightness, palette, and lighting from the slide meaning, readability, and production brief rather than a generic cinematic bias. Unless the brief or user notes clearly call for a dark mood, avoid unnecessarily dark or gloomy styling and keep the result open, readable, and balanced. Do not render user notes, instruction text, measurement text, percentages, labels, interface elements, watermarks, platform-specific layouts, or branding unless they are explicitly part of the provided slide text. Keep the composition centered, readable, and comfortably away from the top and bottom edges.",
    env="IMAGE_SYSTEM_PROMPT",
  )
  system_prompt: str = Field("", env="SYSTEM_PROMPT")
  google_client_id: str = Field("", env="GOOGLE_CLIENT_ID")
  google_client_secret: str = Field("", env="GOOGLE_CLIENT_SECRET")
  google_redirect_uri: str = Field("", env="GOOGLE_REDIRECT_URI")
  frontend_base_url: str = Field("http://localhost:3000", env="FRONTEND_BASE_URL")
  cors_allowed_origins: str = Field(
    "http://localhost:3000,http://127.0.0.1:3000",
    env="CORS_ALLOWED_ORIGINS",
  )
  allow_unauthenticated_generate: bool = Field(True, env="ALLOW_UNAUTHENTICATED_GENERATE")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
  return Settings()
