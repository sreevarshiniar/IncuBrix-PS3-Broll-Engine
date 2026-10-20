
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "IncuBrix B-roll Engine"
    api_prefix: str = "/api/v1"
    data_dir: Path = Path("data")
    outputs_dir: Path = Path("outputs")
    uploads_dir: Path = Path("uploads")

    pexels_api_key: str = ""
    pixabay_api_key: str = ""
    footage_provider: str = "pixabay"

    tts_provider: str = "edge-tts"
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    max_audio_seconds: int = 600
    min_scene_seconds: float = 2.0
    default_fps: int = 30
    log_level: str = "INFO"


settings = Settings()

for directory in (
    settings.data_dir,
    settings.outputs_dir,
    settings.uploads_dir,
):
    directory.mkdir(parents=True, exist_ok=True)
