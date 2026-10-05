from decimal import Decimal
from pathlib import Path
import subprocess
import sys
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import delete

from app.db.session import SessionLocal
from app.main import app
from app.models import TourPackage
from app.repositories import tour_package as repository


client = TestClient(app)
TEST_PREFIX = f"pytest-{uuid4()}"
PROJECT_ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module", autouse=True)
def prepare_database():
    subprocess.run(
        [sys.executable, "-m", "alembic", "upgrade", "head"],
        cwd=PROJECT_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    yield
    with SessionLocal() as db:
        db.execute(delete(TourPackage).where(TourPackage.name.like(f"{TEST_PREFIX}%")))
        db.commit()


def package_payload(name: str, **overrides):
    payload = {
        "name": name,
        "destination": "Goa",
        "description": "Beach and culture tour",
        "duration_days": 4,
        "price": "1200.00",
        "category": "Leisure",
        "itinerary": {"day_1": "Arrival"},
        "inclusions": ["Hotel", "Breakfast"],
        "exclusions": ["Flights"],
        "images": [],
        "availability_status": "available",
    }
    payload.update(overrides)
    return payload


def create_package(name: str, **overrides):
    response = client.post(
        "/api/v1/tour-packages/",
        json=package_payload(name, **overrides),
    )
    assert response.status_code == 201
    return response.json()


def test_post_creates_tour_package():
    response = client.post(
        "/api/v1/tour-packages/",
        json=package_payload(f"{TEST_PREFIX}-create"),
    )

    assert response.status_code == 201
    assert response.json()["name"] == f"{TEST_PREFIX}-create"


def test_duplicate_post_returns_409():
    name = f"{TEST_PREFIX}-duplicate"
    create_package(name)

    response = client.post("/api/v1/tour-packages/", json=package_payload(name))

    assert response.status_code == 409


def test_get_package_by_id():
    created = create_package(f"{TEST_PREFIX}-get")

    response = client.get(f"/api/v1/tour-packages/{created['id']}")

    assert response.status_code == 200
    assert response.json()["id"] == created["id"]


def test_patch_updates_only_supplied_field():
    created = create_package(f"{TEST_PREFIX}-patch")

    response = client.patch(
        f"/api/v1/tour-packages/{created['id']}",
        json={"price": "999.99"},
    )

    data = response.json()
    assert response.status_code == 200
    assert Decimal(data["price"]) == Decimal("999.99")
    assert data["name"] == created["name"]


def test_patch_duplicate_name_destination_returns_409():
    package_a = create_package(
        f"{TEST_PREFIX}-patch-duplicate-a",
        destination="Jaipur",
    )
    package_b = create_package(
        f"{TEST_PREFIX}-patch-duplicate-b",
        destination="Udaipur",
    )

    response = client.patch(
        f"/api/v1/tour-packages/{package_b['id']}",
        json={
            "name": package_a["name"],
            "destination": package_a["destination"],
        },
    )

    assert response.status_code == 409


def test_db_duplicate_rejection_rolls_back_and_allows_next_create(monkeypatch):
    name = f"{TEST_PREFIX}-db-duplicate"
    create_package(name, destination="Bali")
    monkeypatch.setattr(repository, "find_duplicate", lambda *args, **kwargs: None)

    duplicate = client.post(
        "/api/v1/tour-packages/",
        json=package_payload(name.upper(), destination="bali"),
    )
    recovered = client.post(
        "/api/v1/tour-packages/",
        json=package_payload(f"{TEST_PREFIX}-after-rollback", destination="Bali"),
    )

    assert duplicate.status_code == 409
    assert duplicate.json()["detail"] == "Tour package already exists"
    assert recovered.status_code == 201


@pytest.mark.parametrize(
    "payload",
    [
        {"price": "-1.00"},
        {"duration_days": 0},
    ],
)
def test_invalid_price_or_duration_returns_422(payload):
    response = client.post(
        "/api/v1/tour-packages/",
        json=package_payload(f"{TEST_PREFIX}-invalid-{uuid4()}", **payload),
    )

    assert response.status_code == 422


def test_patch_deactivate_sets_is_active_false():
    created = create_package(f"{TEST_PREFIX}-deactivate")

    response = client.patch(f"/api/v1/tour-packages/{created['id']}/deactivate")

    assert response.status_code == 200
    assert response.json()["is_active"] is False


def test_search_list_excludes_inactive_packages():
    active = create_package(f"{TEST_PREFIX}-list-active")
    inactive = create_package(f"{TEST_PREFIX}-list-inactive")
    client.patch(f"/api/v1/tour-packages/{inactive['id']}/deactivate")

    response = client.get(
        "/api/v1/tour-packages/",
        params={"search": f"{TEST_PREFIX}-list"},
    )

    names = {item["name"] for item in response.json()}
    assert response.status_code == 200
    assert active["name"] in names
    assert inactive["name"] not in names


def test_search_by_partial_name_returns_correct_package():
    expected = create_package(f"{TEST_PREFIX}-partial-himalaya")
    create_package(f"{TEST_PREFIX}-partial-desert")

    response = client.get(
        "/api/v1/tour-packages/",
        params={"search": "himalaya"},
    )

    names = {item["name"] for item in response.json()}
    assert response.status_code == 200
    assert expected["name"] in names


def test_combined_filters_return_correct_package():
    expected = create_package(
        f"{TEST_PREFIX}-filters-match",
        destination="Kerala",
        category="Wellness",
        price="1500.00",
        duration_days=6,
        availability_status="seasonal",
    )
    create_package(
        f"{TEST_PREFIX}-filters-miss",
        destination="Kerala",
        category="Adventure",
        price="1500.00",
        duration_days=6,
        availability_status="seasonal",
    )

    response = client.get(
        "/api/v1/tour-packages/",
        params={
            "search": "filters",
            "destination": "kerala",
            "category": "wellness",
            "min_price": "1000.00",
            "max_price": "2000.00",
            "duration_days": 6,
            "availability_status": "SEASONAL",
        },
    )

    names = {item["name"] for item in response.json()}
    assert response.status_code == 200
    assert expected["name"] in names
    assert f"{TEST_PREFIX}-filters-miss" not in names


def test_min_price_greater_than_max_price_returns_422():
    response = client.get(
        "/api/v1/tour-packages/",
        params={"min_price": "2000.00", "max_price": "1000.00"},
    )

    assert response.status_code == 422
    assert response.json()["detail"] == "min_price cannot be greater than max_price"


def test_openapi_schema_exposes_constraints_and_summaries():
    response = client.get("/openapi.json")
    schema = response.json()
    create_schema = schema["components"]["schemas"]["TourPackageCreate"]["properties"]

    assert response.status_code == 200
    assert create_schema["duration_days"]["exclusiveMinimum"] == 0
    assert "minimum" in str(create_schema["price"])
    assert "60000" in str(create_schema["price"])
    assert schema["paths"]["/api/v1/tour-packages/"]["post"]["summary"] == (
        "Create Tour Package"
    )


def test_alembic_upgrade_head_smoke():
    result = subprocess.run(
        [sys.executable, "-m", "alembic", "current"],
        cwd=PROJECT_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )

    assert "20261006_0001" in result.stdout
