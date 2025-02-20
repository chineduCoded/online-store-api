from datetime import datetime
from typing import List, Optional, Dict
from uuid import UUID
from enum import Enum
from decimal import Decimal
from sqlmodel import SQLModel, Field, Column, Numeric
from pydantic import ConfigDict, field_validator
from sqlalchemy.dialects.postgresql import ENUM

class ProductStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    ARCHIVED = "archived"

product_status_enum = ENUM(
    "draft", "active", "archived",
    name="product_status",
)

class ProductBase(SQLModel):
    name: str = Field(index=True, max_length=100)
    description: Optional[str] = Field(default=None, max_length=500)
    base_price: Decimal = Field(
        default=Decimal(0.0),
        sa_column=Column(Numeric(10, 2), nullable=False)
    )
    status: ProductStatus = Field(
        sa_column=Column(
            product_status_enum,
            nullable=False,
            server_default=ProductStatus.DRAFT.value
        )
    )

class ProductCreate(ProductBase):
    variants: Optional[List["ProductVariantCreate"]] = None
    images: Optional[List["ProductImageCreate"]] = None
    # Use a list of UUID to associate existing categories
    categories_ids: Optional[List[UUID]] = None

class ProductReadBase(SQLModel):
    id: UUID
    name: str
    description: Optional[str] = None
    base_price: Decimal
    status: ProductStatus
    created_at: datetime
    updated_at: Optional[datetime] = None
    model_config = ConfigDict(
        from_attributes=True,
        arbitrary_types_allowed=True
    )

class ProductRead(ProductReadBase):
    variants: List["ProductVariantRead"] = []
    images: List["ProductImageRead"] = []
    categories: List["CategoryRead"] = []

    model_config = ConfigDict(
        json_encoders = {
            Decimal: lambda v: str(v)
        }
    )

class ProductUpdate(SQLModel):
    name: Optional[str] = None
    description: Optional[str] = None
    base_price: Optional[Decimal] = None
    status: Optional[ProductStatus] = None

class ProductVariantCreate(SQLModel):
    product_id: UUID
    sku: str
    attributes: Optional[Dict[str, str]] = {}
    price_offset: Optional[Decimal] = 0.00
    stock_quantity: int

class ProductVariantRead(SQLModel):
    id: UUID
    sku: str
    attributes: Dict[str, str]
    price_offset: Decimal
    stock_quantity: int
    final_price: Decimal  # Include computed property
    model_config = ConfigDict(
        from_attributes=True,
        arbitrary_types_allowed=True
    )

class ProductVariantUpdate(SQLModel):
    sku: Optional[str] = Field(default=None, max_length=50)
    attributes: Optional[Dict[str, str]] = None
    price_offset: Optional[Decimal] = Field(default=None, max_digits=10, decimal_places=2)
    stock_quantity: Optional[int] = Field(default=None, ge=0)

class ProductImageCreate(SQLModel):
    product_id: UUID
    image_url: str
    image_alt: str
    caption: Optional[str] = None
    sort_order: Optional[int] = 0

class ProductImageRead(SQLModel):
    id: UUID
    product_id: UUID
    image_url: str
    image_alt: str
    caption: Optional[str] = None
    sort_order: int
    model_config = ConfigDict(
        from_attributes=True,
        arbitrary_types_allowed=True
    )

class ProductImageUpdate(SQLModel):
    image_url: Optional[str] = Field(default=None, max_length=500)
    image_alt: Optional[str] = Field(default=None, max_length=100)
    caption: Optional[str] = Field(default=None, max_length=100)
    sort_order: Optional[int] = Field(default=None)

class CategoryCreate(SQLModel):
    name: str
    parent_id: Optional[UUID] = None

    @field_validator("name")
    def validate_name(cls, v):
        if not v:
            raise ValueError("Category name cannot be empty")
        return v


class CategoryUpdate(SQLModel):
    name: Optional[str] = None
    parent_id: Optional[UUID] = None

class CategoryRead(SQLModel):
    id: UUID
    name: str
    parent_id: Optional[UUID] = None
    model_config = ConfigDict(
        from_attributes=True,
        arbitrary_types_allowed=True
    )


ProductRead.model_rebuild()
ProductVariantRead.model_rebuild()
ProductImageRead.model_rebuild()
CategoryRead.model_rebuild()