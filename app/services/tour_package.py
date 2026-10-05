
from decimal import Decimal
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.tour_package import TourPackage
from app.repositories import tour_package as repository
from app.schemas.tour_package import TourPackageCreate, TourPackageUpdate


def create_package(db: Session, data: TourPackageCreate) -> TourPackage:
    duplicate = repository.find_duplicate(db, data.name, data.destination)
    if duplicate:
        raise ValueError("Tour package already exists")
    return repository.create(db, data)


def get_package(db: Session, package_id: UUID) -> TourPackage:
    tour_package = repository.get_by_id(db, package_id)
    if tour_package is None:
        raise LookupError("Tour package not found")
    return tour_package


def update_package(
    db: Session,
    package_id: UUID,
    data: TourPackageUpdate,
) -> TourPackage:
    tour_package = repository.get_by_id(db, package_id)
    if tour_package is None:
        raise LookupError("Tour package not found")

    changes = data.model_dump(exclude_unset=True)
    name = changes.get("name", tour_package.name)
    destination = changes.get("destination", tour_package.destination)
    duplicate = repository.find_duplicate(
        db,
        name,
        destination,
        exclude_id=tour_package.id,
    )
    if duplicate:
        raise ValueError("Tour package already exists")

    return repository.update(db, tour_package, data)


def deactivate_package(db: Session, package_id: UUID) -> TourPackage:
    tour_package = repository.get_by_id(db, package_id)
    if tour_package is None:
        raise LookupError("Tour package not found")
    if not tour_package.is_active:
        return tour_package
    return repository.deactivate(db, tour_package)


def search_packages(
    db: Session,
    search: str | None = None,
    destination: str | None = None,
    category: str | None = None,
    min_price: Decimal | None = None,
    max_price: Decimal | None = None,
    duration_days: int | None = None,
    availability_status: str | None = None,
) -> list[TourPackage]:
    return repository.search(
        db=db,
        search=search,
        destination=destination,
        category=category,
        min_price=min_price,
        max_price=max_price,
        duration_days=duration_days,
        availability_status=availability_status,
    )
