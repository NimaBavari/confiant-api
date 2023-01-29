import pytest

from main import app


@pytest.fixture(scope="module")
def client():
    with app.test_client() as client:
        yield client


def test_without_query_params(client):
    rv = client.get("/search")
    assert rv.status_code == 400


def test_with_missing_query_params(client):
    rv = client.get("/search?keyword=license&smth=something")
    assert rv.status_code == 400


def test_with_too_many_query_params(client):
    rv = client.get("/search?keyword=license&language=javascript&smth=something")
    assert rv.status_code == 400


def test_with_strange_language_in_query_params(client):
    rv = client.get("/search?keyword=license&language=golang")
    assert rv.status_code == 401


def test_with_just_right_query_params(client):
    rv = client.get("/search?keyword=license&language=javascript")
    assert rv.status_code == 200
