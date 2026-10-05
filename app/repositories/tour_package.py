
from decimal import Decimal
from uuid import UUID

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.models.tour_package import TourPackage
from app.schemas.tour_package import TourPackageCreate, TourPackageUpdate


def get_by_id(db: Session, package_id: UUID) -> TourPackage | None:
    return db.scalar(select(TourPackage).where(TourPackage.id == package_id))


def find_duplicate(
    db: Session,
    name: str,
    destination: str,
    exclude_id: UUID | None = None,
) -> TourPackage | None:
    stmt = select(TourPackage).where(
        func.lower(TourPackage.name) == name.lower(),
        func.lower(TourPackage.destination) == destination.lower(),
    )
    if exclude_id is not None:
        stmt = stmt.where(TourPackage.id != exclude_id)
    return db.scalar(stmt)


def create(db: Session, data: TourPackageCreate) -> TourPackage:
    tour_package = TourPackage(**data.model_dump())
    db.add(tour_package)
    db.commit()
    db.refresh(tour_package)
    return tour_package


def update(
    db: Session,
    package: TourPackage,
    data: TourPackageUpdate,
) -> TourPackage:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(package, field, value)
    db.commit()
    db.refresh(package)
    return package


def deactivate(db: Session, package: TourPackage) -> TourPackage:
    package.is_active = False
    db.commit()
    db.refresh(package)
    return package


def search(
    db: Session,
    search: str | None = None,
    destination: str | None = None,
    category: str | None = None,
    min_price: Decimal | None = None,
    max_price: Decimal | None = None,
    duration_days: int | None = None,
    availability_status: str | None = None,
) -> list[TourPackage]:
    stmt = select(TourPackage).where(TourPackage.is_active.is_(True))

    if search:
        term = f"%{search.lower()}%"
        stmt = stmt.where(
            or_(
                func.lower(TourPackage.name).like(term),
                func.lower(TourPackage.destination).like(term),
            )
        )
    if destination:
        stmt = stmt.where(func.lower(TourPackage.destination) == destination.lower())
    if category:
        stmt = stmt.where(func.lower(TourPackage.category) == category.lower())
    if min_price is not None:
        stmt = stmt.where(TourPackage.price >= min_price)
    if max_price is not None:
        stmt = stmt.where(TourPackage.price <= max_price)
    if duration_days is not None:
        stmt = stmt.where(TourPackage.duration_days == duration_days)
    if availability_status:
        stmt = stmt.where(
            func.lower(TourPackage.availability_status) == availability_status.lower()
        )

    return list(db.scalars(stmt).all())
