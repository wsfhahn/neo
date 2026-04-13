from app.common.generation import generate_response
from pydantic import BaseModel, Field
from rich import print


class IntroductionResponse(BaseModel):
    """An introduction to the user from the AI assistant."""
    name: str = Field(..., description="The identity of the AI assistant")
    bio: str = Field(..., description="A short bio about the AI assistant (1-3 sentences)")


response = generate_response(
    user_message="Who are you?",
    system_message=None,
    response_format=IntroductionResponse,
    model_id=None
)


print(response)