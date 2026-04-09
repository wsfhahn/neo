from typing import Self
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import model_validator
from pathlib import Path
import os
from openai import (
    OpenAI,
    APIConnectionError
)

from app.common.errors import (
    InvalidAPIHostError,
    InvalidSamplingParameterError,
    InvalidModelIDError,
    InvalidSavePathError
)


class Settings(BaseSettings):
    api_host: str
    model_id: str
    save_dir: Path
    temperature: float = 1.0
    top_k: int = 64
    top_p: float = 1.0
    min_p: float = 0.0

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8"
    )

    @model_validator(mode="after")
    def validate_model(self) -> Self:
        if self.temperature < 0.0 or self.temperature > 2.0:
            raise InvalidSamplingParameterError(
                param="temperature",
                reason="must be between 0.0 and 2.0 (inclusive)"
            )
        elif self.top_k < 1 or self.top_k > 128:
            raise InvalidSamplingParameterError(
                param="top_k",
                reason="must be between 1 and 128 (inclusive)"
            )
        elif self.top_p <= 0.0 or self.top_p > 1.0:
            raise InvalidSamplingParameterError(
                param="top_p",
                reason="top_p must be positive and <= 1.0"
            )
        elif self.min_p < 0.0 or self.min_p > 1.0:
            raise InvalidSamplingParameterError(
                param="min_p",
                reason="min_p must be greater than 0.0 and less than 1.0 (inclusive)"
            )
        elif self.save_dir.exists() and not self.save_dir.is_dir():
            raise InvalidSavePathError(
                path_str=str(self.save_dir),
                reason="save_dir cannot point to a file"
            )

        test_client = OpenAI(
            base_url=self.api_host,
            api_key=""
        )

        try:
            valid_models = [m.id for m in test_client.models.list().data]
        except APIConnectionError as e:
            raise InvalidAPIHostError(
                api_host=self.api_host,
                reason="failed to connect"
            )
        
        if self.model_id not in valid_models:
            raise InvalidModelIDError(model_id=self.model_id)
        
        if not self.save_dir.exists():
            os.mkdir(self.save_dir)
        
        return self
        

GLOBAL_SETTINGS = Settings() # type: ignore
GLOBAL_CLIENT = OpenAI(
    base_url=GLOBAL_SETTINGS.api_host,
    api_key=""
)