import os
from dotenv import load_dotenv
from pydantic_ai import Agent
from pydantic_ai.models.openrouter import OpenRouterModel
from pydantic_ai.providers.openrouter import OpenRouterProvider

load_dotenv()


def create_agent(model_name: str = "openrouter/free", **kwargs) -> Agent:
    model = OpenRouterModel(
        model_name,
        provider=OpenRouterProvider(api_key=os.getenv("OPENROUTER_API_KEY")),
    )
    return Agent(model, **kwargs)
