import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import model_validator, field_validator
from pathlib import Path
from typing import Self
from openai import (
    OpenAI,
    APIConnectionError,
    AuthenticationError
)

from app.common.errors import (
    UnreachableHostError,
    InvalidAPIKeyError,
    InvalidModelIDError,
    InvalidSamplingParameterError,
    InvalidSaveDir
)


class Settings(BaseSettings):
    api_host: str
    api_key: str = "none"
    save_dir: Path = Path("storage")

    default_model_id: str
    temperature: float = 1.0
    top_k: int = 64
    top_p: float = 1.0
    min_p: float = 0.0

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8"
    )

    @field_validator("save_dir")
    @classmethod
    def validate_save_dir(cls, save_dir: Path) -> Path:
        if save_dir.exists() and not save_dir.is_dir():
            raise InvalidSaveDir(
                path_str=str(save_dir),
                reason="save_dir cannot point to a file"
            )
        return save_dir
    
    @field_validator("temperature")
    @classmethod
    def validate_temperature(cls, temperature: float) -> float:
        if temperature < 0.0 or temperature > 3.0:
            raise InvalidSamplingParameterError(
                param="temperature",
                value=temperature,
                reason="must be >= 0.0 and <= 3.0"
            )
        return temperature
    
    @field_validator("top_k")
    @classmethod
    def validate_top_k(cls, top_k: int) -> int:
        if top_k <= 0 or top_k > 128:
            raise InvalidSamplingParameterError(
                param="top_k",
                value=top_k,
                reason="must be > 0 and <= 128"
            )
        return top_k
    
    @field_validator("top_p")
    @classmethod
    def validate_top_p(cls, top_p: float) -> float:
        if top_p <= 0.0 or top_p > 1.0:
            raise InvalidSamplingParameterError(
                param="top_p",
                value=top_p,
                reason="top_p must be > 0.0 and <= 1.0"
            )
        return top_p
    
    @field_validator("min_p")
    @classmethod
    def validate_min_p(cls, min_p: float) -> float:
        if min_p < 0.0 or min_p > 0.4:
            raise InvalidSamplingParameterError(
                param="min_p",
                value=min_p,
                reason="min_p must be >= 0.0 and <= 0.4"
            )
        return min_p

    @model_validator(mode='after')
    def validate_cross_fields(self) -> Self:
        test_client = OpenAI(
            base_url=self.api_host,
            api_key=self.api_key
        )

        try:
            valid_models = [m.id for m in test_client.models.list()]
        except APIConnectionError:
            raise UnreachableHostError(self.api_host)
        except AuthenticationError:
            raise InvalidAPIKeyError
        
        if self.default_model_id not in valid_models:
            raise InvalidModelIDError(self.default_model_id)
        
        if not self.save_dir.exists():
            os.mkdir(self.save_dir)
        
        return self
    

GLOBAL_SETTINGS = Settings() # type: ignore[call-arg]
GLOBAL_CLIENT = OpenAI(
    base_url=GLOBAL_SETTINGS.api_host,
    api_key=GLOBAL_SETTINGS.api_key
)