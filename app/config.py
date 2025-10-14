from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DB_URL: str = "sqlite:///./test.db"
    ALLOWED_TABLES: list[str] = ["news", "supplier"]
    SERVICENOW_SERVICE_URL: str = "http://localhost:8001"
    SERVICE_MANAGER_API_URL: str
    SERVICENOW_USERNAME: str
    SERVICENOW_PASSWORD: str

    GLPI_SERVICE_URL: str = "http://localhost:8002"
    GLPI_API_URL: str
    GLPI_APP_TOKEN: str
    GLPI_ACCESS_TOKEN: str
    GLPI_USERNAME: str
    GLPI_PASSWORD: str

    FILE_SERVICE_URL: str = "http://file_service:8003"

settings = Settings()