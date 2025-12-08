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

    # OpenAI / AI Logic
    OPENAI_API_KEY: str = ""

    class Config:
        case_sensitive = True

settings = Settings()
