
import uuid
from datetime import datetime
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class TourPackageCreate(BaseModel):
    name: str
    destination: str
    description: str
    duration_days: int = Field(gt=0)
    price: Decimal = Field(ge=0)
    category: str
    itinerary: dict[str, Any]
    inclusions: list[str]
    exclusions: list[str]
    images: list[str] = Field(default_factory=list)
    availability_status: str


class TourPackageUpdate(BaseModel):
    name: str | None = None
    destination: str | None = None
    description: str | None = None
    duration_days: int | None = Field(default=None, gt=0)
    price: Decimal | None = Field(default=None, ge=0)
    category: str | None = None
    itinerary: dict[str, Any] | None = None
    inclusions: list[str] | None = None
    exclusions: list[str] | None = None
    images: list[str] | None = None
    availability_status: str | None = None


class TourPackageRead(BaseModel):
    id: uuid.UUID
    name: str
    destination: str
    description: str
    duration_days: int
    price: Decimal
    category: str
    itinerary: dict[str, Any]
    inclusions: list[str]
    exclusions: list[str]
    images: list[str]
    availability_status: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
