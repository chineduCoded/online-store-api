from sqlmodel import SQLModel, Field, Relationship, Column, UUID as SQLModelUUID, text, Numeric, ForeignKey
from datetime import datetime
from decimal import Decimal
from uuid import UUID
from typing import Optional, List, TYPE_CHECKING
from app.utils.datetime_now import datetime_now
from app.schemas.order_schema import OrderBase, OrderStatus

if TYPE_CHECKING:
    from app.models import Payment, PaymentStatus
    from app.models import ProductVariant

class Order(OrderBase, table=True):
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
    payments: List["Payment"] = Relationship(
        back_populates="order",
        sa_relationship_kwargs={
            "cascade": "all, delete-orphan",
            "passive_deletes": True
        }
    )
    items: List["OrderItem"] = Relationship(
        back_populates="order",
        sa_relationship_kwargs={
            "cascade": "all, delete-orphan",
            "passive_deletes": True
        }
    )

    def update_status(self, status: OrderStatus):
        self.status = status
        self.updated_at = datetime_now()

    def add_payment(self, payment: "Payment") -> "Payment":
        self.payments.append(payment)
        return payment

    def calculate_total_paid(self) -> Decimal:
        return sum(p.amount for p in self.payments if p.status == PaymentStatus.SUCCESS)

    def calculate_total_refunded(self) -> Decimal:
        return sum(p.amount for p in self.payments if p.status == PaymentStatus.REFUNDED)

    @property
    def total_due(self) -> Decimal:
        return self.total_amount - self.calculate_total_paid()

    @property
    def is_fully_paid(self) -> bool:
        return self.total_due <= Decimal(0)

class OrderItem(SQLModel, table=True):
    id: Optional[UUID] = Field(
        default=None,
        sa_column=Column(
            SQLModelUUID(as_uuid=True),
            primary_key=True,
            server_default=text("gen_random_uuid()")
        )
    )
    order_id: UUID = Field(
        sa_column=Column(
            SQLModelUUID(as_uuid=True),
            ForeignKey("order.id", ondelete="CASCADE"),
            nullable=False
        )
    )
    variant_id: UUID = Field(
        sa_column=Column(
            SQLModelUUID(as_uuid=True),
            ForeignKey("product_variant.id", ondelete="SET NULL"),
            nullable=True
        ) # Keep order history even if variant is archived
    )
    quantity: int = Field(ge=1, default=1)
    price_at_purchase: Decimal = Field(
        default=Decimal(0.0),
        sa_column=Column(Numeric(10, 2), nullable=False)
    )

    order: Order = Relationship(back_populates="items")
    variant: "ProductVariant" = Relationship(back_populates="order_items")

    @property
    def total_price(self) -> Decimal:
        return self.price_at_purchase * self.quantity
