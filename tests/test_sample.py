import pytest
from src.api import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_create_user(client):
    # Test creazione utente
    user_data = {"projects": ["CERRI"]}

    response = client.post(
        "/infra_utils/fetch_rack_slot_type_by_project", json=user_data
    )

    assert response.status_code == 200
