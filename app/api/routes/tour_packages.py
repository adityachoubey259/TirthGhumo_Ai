
from decimal import Decimal
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.tour_package import (
    TourPackageCreate,
    TourPackageRead,
    TourPackageUpdate,
)
from app.services import tour_package as service


router = APIRouter(prefix="/api/v1/tour-packages", tags=["Tour Packages"])


@router.post("/", response_model=TourPackageRead, status_code=status.HTTP_201_CREATED)
def create_tour_package(
    data: TourPackageCreate,
    db: Session = Depends(get_db),
) -> TourPackageRead:
    try:
        return service.create_package(db, data)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc


@router.get("/", response_model=list[TourPackageRead])
def search_tour_packages(
    search: str | None = None,
    destination: str | None = None,
    category: str | None = None,
    min_price: Decimal | None = Query(default=None, ge=0),
    max_price: Decimal | None = Query(default=None, ge=0),
    duration_days: int | None = Query(default=None, gt=0),
    availability_status: str | None = None,
    db: Session = Depends(get_db),
) -> list[TourPackageRead]:
    if min_price is not None and max_price is not None and min_price > max_price:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="min_price cannot be greater than max_price",
        )
    return service.search_packages(
        db=db,
        search=search,
        destination=destination,
        category=category,
        min_price=min_price,
        max_price=max_price,
        duration_days=duration_days,
        availability_status=availability_status,
    )


@router.get("/{package_id}", response_model=TourPackageRead)
def get_tour_package(
    package_id: UUID,
    db: Session = Depends(get_db),
) -> TourPackageRead:
    try:
        return service.get_package(db, package_id)
    except LookupError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.patch("/{package_id}", response_model=TourPackageRead)
def update_tour_package(
    package_id: UUID,
    data: TourPackageUpdate,
    db: Session = Depends(get_db),
) -> TourPackageRead:
    try:
        return service.update_package(db, package_id, data)
    except LookupError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc


@router.patch("/{package_id}/deactivate", response_model=TourPackageRead)
def deactivate_tour_package(
    package_id: UUID,
    db: Session = Depends(get_db),
) -> TourPackageRead:
    try:
        return service.deactivate_package(db, package_id)
    except LookupError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
