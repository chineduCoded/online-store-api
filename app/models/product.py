from decimal import Decimal
from datetime import datetime
from uuid import UUID
from typing import Optional, List, Dict, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship, Column, UUID as SQLModelUUID, text, JSON, Column, Numeric, ForeignKey
from app.utils.datetime_now import datetime_now
from app.schemas.product_schema import ProductBase, ProductStatus

if TYPE_CHECKING:
    from app.models import OrderItem

class ProductCategory(SQLModel, table=True):
    product_id: UUID = Field( 
        sa_column=Column(
            SQLModelUUID(as_uuid=True),
            ForeignKey("product.id", ondelete="CASCADE"),
            primary_key=True
        )
    )
    category_id: UUID = Field( 
        sa_column=Column(
            SQLModelUUID(as_uuid=True),
            ForeignKey("category.id", ondelete="CASCADE"),
            primary_key=True
        )
    )

class Product(ProductBase, table=True):
    id: Optional[UUID] = Field(
        default=None,
        sa_column=Column(
            SQLModelUUID(as_uuid=True),
            primary_key=True,
            server_default=text("gen_random_uuid()")
        )
    )
    created_at: datetime = Field(default_factory=datetime_now)
    updated_at: Optional[datetime] = Field(default=None)

    # Relationships
    variants: List["ProductVariant"] = Relationship(
        back_populates="product",
        sa_relationship_kwargs={
            "cascade": "all, delete-orphan",
            "passive_deletes": True
        }
    )
    images: List["ProductImage"] = Relationship(
        back_populates="product",
        sa_relationship_kwargs={
            "cascade": "all, delete-orphan",
            "passive_deletes": True
        }
    )
    categories: List["Category"] = Relationship(
        back_populates="products",
        link_model=ProductCategory,
        sa_relationship_kwargs={
            "cascade": "all, delete",
            "passive_deletes": True
        }
    )

    def update_status(self, status: ProductStatus):
        self.status = status
        self.updated_at = datetime_now()

    def update_price(self, price: Decimal):
        self.base_price = price
        self.updated_at = datetime_now()

    def get_main_image(self) -> Optional["ProductImage"]:
        return next((img for img in sorted(self.images, key=lambda x: x.sort_order)), None)
    
    @property
    def is_available(self) -> bool:
        return self.status == ProductStatus.ACTIVE
    
    @property
    def is_archived(self) -> bool:
        return self.status == ProductStatus.ARCHIVED
    
    def archive(self):
        self.update_status(ProductStatus.ARCHIVED)

        for variant in self.variants:
            variant.archive()
    
class Category(SQLModel, table=True):
    id: Optional[UUID] = Field(
        default=None,
        sa_column=Column(
            SQLModelUUID(as_uuid=True),
            primary_key=True,
            server_default=text("gen_random_uuid()")
        )
    )
    name: str = Field(index=True, max_length=50)
    parent_id: Optional[UUID] = Field(default=None, foreign_key="category.id")
    
    products: List["Product"] = Relationship(
        back_populates="categories",
        link_model=ProductCategory,
        sa_relationship_kwargs={
            "cascade": "all, delete",
            "passive_deletes": True
        }
    )

class ProductVariant(SQLModel, table=True):
    __tablename__ = "product_variant"
    id: Optional[UUID] = Field(
        default=None,
        sa_column=Column(
            SQLModelUUID(as_uuid=True),
            primary_key=True,
            server_default=text("gen_random_uuid()")
        ),
    )
    product_id: UUID = Field(
        sa_column=Column(
            SQLModelUUID(as_uuid=True),
            ForeignKey("product.id", ondelete="CASCADE")
        )
    )
    sku: str = Field(unique=True, index=True, max_length=50)
    attributes: Dict[str, str] = Field(
        sa_column=Column(JSON),
        default={}
    )
    price_offset: Decimal = Field(
        default=Decimal(0.0),
        sa_column=Column(Numeric(10, 2), nullable=False)
    )
    stock_quantity: int = Field(default=0, ge=0)

    product: Product = Relationship(back_populates="variants")
    order_items: List["OrderItem"] = Relationship(back_populates="variant")
    status: ProductStatus = Field(default=ProductStatus.ACTIVE)

    def archive(self):
        self.status = ProductStatus.ARCHIVED
        self.stock_quantity = 0

    @property
    def final_price(self) -> Decimal:
        return self.product.base_price + self.price_offset
    
    def adjust_stock(self, quantity: int):
        if self.stock_quantity + quantity < 0:
            raise ValueError("Insufficient stock")
        self.stock_quantity += quantity

    @property
    def is_in_stock(self) -> bool:
        return self.stock_quantity > 0

class ProductImage(SQLModel, table=True):
    id: Optional[UUID] = Field(
        default=None,
        sa_column=Column(
            SQLModelUUID(as_uuid=True),
            primary_key=True,
            server_default=text("gen_random_uuid()")
        )
    )
    product_id: UUID = Field(
        sa_column=Column(
            SQLModelUUID(as_uuid=True),
            ForeignKey("product.id", ondelete="CASCADE")
        )
    )
    image_url: str = Field(max_length=500)
    image_alt: str = Field(max_length=100)
    caption: Optional[str] = Field(default=None, max_length=100)
    sort_order: int = Field(default=0)
    
    product: Product = Relationship(back_populates="images")

    def set_as_primary(self):
        self.sort_order = 0
        for img in self.product.images:
            if img.id != self.id:
                img.sort_order += 1