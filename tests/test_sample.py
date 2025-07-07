import sys
import os

print(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import pytest
from src.api import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_fetch_rack_slot_type_by_project(client):
    # Test fetch_rack_slot_type_by_project
    user_data = {"projects": ["CERRI"]}

    response = client.post(
        "/infra_utils/fetch_rack_slot_type_by_project", json=user_data
    )

    assert response.status_code == 200

def test_failing_fetch_rack_slot_type_by_project(client):
    # Test fetch_rack_slot_type_by_project
    user_data = {"projects": ["pippo"]}

    response = client.post(
        "/infra_utils/fetch_rack_slot_type_by_project", json=user_data
    )

    assert response.status_code == 400
