from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DB_URL: str = "sqlite:///./test.db"
    ALLOWED_TABLES: list[str] = ["news", "supplier"]
    SERVICE_MANAGER_API_URL: str
    SERVICENOW_USERNAME: str
    SERVICENOW_PASSWORD: str

settings = Settings()