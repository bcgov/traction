import pytest

from api.main import app
from fastapi.testclient import TestClient

client = TestClient(app)
