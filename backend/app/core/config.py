from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Agentic Contract Negotiator"
    API_V1_STR: str = "/api/v1"
    
    # Database
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "negotiator"
    SQLALCHEMY_DATABASE_URI: str | None = None

    # LLM Settings
    LLM_PROVIDER: str = "aws"  # aws or mistral
    
    # AWS Bedrock
    AWS_REGION: str = "eu-central-1"
    AWS_BEDROCK_MODEL_ID: str = "anthropic.claude-3-5-sonnet-20240620-v1:0"
    AWS_ACCESS_KEY_ID: str | None = None
    AWS_SECRET_ACCESS_KEY: str | None = None

    # Mistral AI
    MISTRAL_API_KEY: str | None = None
    MISTRAL_MODEL_ID: str = "mistral-large-latest"

    # OpenAI (Legacy/Global)
    OPENAI_API_KEY: str = ""

    class Config:
        case_sensitive = True

settings = Settings()
