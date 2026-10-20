from pydantic import BaseModel, Field, HttpUrl, model_validator
from typing import Literal

class SceneInput(BaseModel):
    text: str = Field(min_length=1, max_length=2000)
    visual_hint: str | None = None

class CaptionsConfig(BaseModel):
    burn_in: bool = True
    srt: bool = True

class JobRequest(BaseModel):
    audio_url: HttpUrl | None = None
    script: str | None = Field(default=None, max_length=20000)
    scenes: list[SceneInput] | None = None
    voice: str = "en-IN-female"
    aspect_ratios: list[Literal["16:9", "9:16", "1:1"]] = ["16:9"]
    style: str = "bright, modern, real-world footage"
    avoid: list[str] = []
    captions: CaptionsConfig = CaptionsConfig()

    @model_validator(mode="after")
    def require_input(self):
        if not (self.audio_url or self.script or self.scenes):
            raise ValueError("Provide audio_url, script, or scenes")
        if self.audio_url and (self.script or self.scenes):
            raise ValueError("Provide only one input type: audio_url, script, or scenes")
        if not self.aspect_ratios:
            raise ValueError("At least one aspect ratio is required")
        return self

class JobAccepted(BaseModel):
    job_id: str
    status: str
    status_url: str

class ErrorBody(BaseModel):
    code: str
    message: str
    retryable: bool = False
    details: dict = {}
