from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DB_URL: str = "sqlite:///./test.db"
    ALLOWED_TABLES: list[str] = ["news", "supplier"]
    GLPI_API_URL: str
    GLPI_APP_TOKEN: str
    GLPI_USERNAME: str
    GLPI_PASSWORD: str

settings = Settings()