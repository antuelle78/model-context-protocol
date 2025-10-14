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
    APIs: List[ApiConfig] = []

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
