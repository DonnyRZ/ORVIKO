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
  system_prompt: str = Field(
    "You are a visual slide designer. Create a 9:16 slide image (1080x1920). "
    "The slide text is the source of truth and must be used exactly and completely. "
    "Determine the layout and design based on the text context. If user notes are provided, "
    "treat them as guidance for style or context only and do not render them as visible text. "
    "Keep the layout clean, readable, and suitable for TikTok slides with minimal background noise. "
    "Keep all important text and visuals "
    "within the vertical safe area: leave at least 8-10% top and bottom margin to avoid "
    "TikTok UI overlays. Center the composition vertically and avoid placing text near the "
    "extreme top/bottom. If embed images are provided, integrate all of them contextually so "
    "they fit the text and overall composition. If no embed images are provided, include simple supportive "
    "visuals or infographics consistent with the design. Avoid adding extra text beyond the "
    "provided slide text.",
    env="SYSTEM_PROMPT",
  )
  cors_allowed_origins: str = Field(
    "http://localhost:3000,http://127.0.0.1:3000",
    env="CORS_ALLOWED_ORIGINS",
  )
  allow_unauthenticated_generate: bool = Field(True, env="ALLOW_UNAUTHENTICATED_GENERATE")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
  return Settings()
