from decimal import Decimal
from enum import Enum
from sqlmodel import SQLModel, Field, Column, Numeric
from sqlalchemy.dialects.postgresql import ENUM

order_status_enum = ENUM(
    "pending", "confirmed", "processing", "delivered", "cancelled",
    name="order_status",
)

class OrderStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PROCESSING = "processing"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"

class OrderBase(SQLModel):
    total_amount: Decimal = Field(
        default=Decimal(0.0),
        sa_column=Column(Numeric(10, 2), nullable=False)
    )
    status: OrderStatus = Field(
        sa_column=Column(
            order_status_enum,
            nullable=False,
            server_default=OrderStatus.PENDING.value
        )
    )
    shipping_address: str