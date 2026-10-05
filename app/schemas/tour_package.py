
import uuid
from datetime import datetime
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class TourPackageCreate(BaseModel):
    name: str = Field(description="Tour package name", examples=["Bali Adventure"])
    destination: str = Field(description="Primary destination", examples=["Bali"])
    description: str = Field(
        description="Package overview",
        examples=["A 5-day Bali adventure with temples, beaches, and local tours."],
    )
    duration_days: int = Field(description="Trip duration in days", gt=0, examples=[5])
    price: Decimal = Field(
        description="Package price",
        ge=0,
        max_digits=10,
        decimal_places=2,
        examples=["60000.00"],
    )
    category: str = Field(description="Package category", examples=["International"])
    itinerary: dict[str, Any] = Field(
        description="Day-wise itinerary",
        examples=[{"day_1": "Arrival and beach walk"}],
    )
    inclusions: list[str] = Field(
        description="Included services",
        examples=[["Hotel", "Breakfast", "Airport pickup"]],
    )
    exclusions: list[str] = Field(
        description="Excluded services",
        examples=[["Flights", "Visa fees"]],
    )
    images: list[str] = Field(
        default_factory=list,
        description="Image URLs",
        examples=[["https://example.com/bali.jpg"]],
    )
    availability_status: str = Field(
        description="Availability status",
        examples=["available"],
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Bali Adventure",
                "destination": "Bali",
                "description": "A 5-day Bali adventure with temples and beaches.",
                "duration_days": 5,
                "price": "60000.00",
                "category": "International",
                "itinerary": {"day_1": "Arrival", "day_2": "Temple tour"},
                "inclusions": ["Hotel", "Breakfast"],
                "exclusions": ["Flights"],
                "images": ["https://example.com/bali.jpg"],
                "availability_status": "available",
            }
        }
    )


class TourPackageUpdate(BaseModel):
    name: str | None = Field(default=None, examples=["Bali Adventure"])
    destination: str | None = Field(default=None, examples=["Bali"])
    description: str | None = Field(default=None, examples=["Updated package details."])
    duration_days: int | None = Field(default=None, gt=0, examples=[5])
    price: Decimal | None = Field(
        default=None,
        ge=0,
        max_digits=10,
        decimal_places=2,
        examples=["60000.00"],
    )
    category: str | None = Field(default=None, examples=["International"])
    itinerary: dict[str, Any] | None = Field(
        default=None,
        examples=[{"day_1": "Arrival and check-in"}],
    )
    inclusions: list[str] | None = Field(default=None, examples=[["Hotel"]])
    exclusions: list[str] | None = Field(default=None, examples=[["Flights"]])
    images: list[str] | None = Field(
        default=None,
        examples=[["https://example.com/bali.jpg"]],
    )
    availability_status: str | None = Field(default=None, examples=["available"])


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
