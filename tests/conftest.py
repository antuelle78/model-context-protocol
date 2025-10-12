import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

os.environ["SERVICENOW_USERNAME"] = "testuser"
os.environ["SERVICENOW_PASSWORD"] = "testpassword"
os.environ["SERVICE_MANAGER_API_URL"] = "http://servicenow.example.com/api"
os.environ["GLPI_API_URL"] = "http://localhost:8081/glpi/apirest.php"
os.environ["GLPI_APP_TOKEN"] = "test_app_token"
os.environ["GLPI_USERNAME"] = "testuser"
os.environ["GLPI_PASSWORD"] = "testpassword"

from app.main import app
from app.models import Base
from app.database import get_db

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="function")
def client():
    Base.metadata.create_all(bind=engine)
    yield TestClient(app)
    Base.metadata.drop_all(bind=engine)