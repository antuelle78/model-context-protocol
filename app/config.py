from pydantic import BaseModel
from pydantic_settings import BaseSettings
from typing import List

class ApiConfig(BaseModel):
    name: str
    base_url: str
    openapi_url: str
    auth_type: str
    auth_key: str = None
    auth_user: str = None
    auth_pass: str = None

class Settings(BaseSettings):
    DB_URL: str = "sqlite:///./test.db"
    OPENWEATHER_API_KEY: str = "5ae241049876bed269426796221a6002"
    ALPHAVANTAGE_API_KEY: str = "3TQ35HGSYS0MOMYX"
    APIs: List[ApiConfig] = []

    GLPI_API_URL: str = "http://mock_glpi_api:8081/glpi/apirest.php"
    GLPI_APP_TOKEN: str = "dummy-app-token"
    GLPI_USERNAME: str = "dummy-user"
    GLPI_PASSWORD: str = "dummy-password"
    GLPI_ACCESS_TOKEN: str = "dummy-access-token"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
