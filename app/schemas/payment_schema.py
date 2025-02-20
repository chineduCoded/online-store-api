from enum import Enum
from decimal import Decimal
from typing import Optional
from sqlmodel import SQLModel, Field, Column, Numeric
from uuid import UUID
from sqlalchemy.dialects.postgresql import ENUM

payment_status_enum = ENUM(
    "pending", "success", "failed", "refunded",
    name="payment_status",
)


class PaymentMethod(str, Enum):
    CREDIT_CARD = "credit_card"
    CASH_ON_DELIVERY = "cod"

class PaymentStatus(str, Enum):
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"
    REFUNDED = "refunded"

class PaymentBase(SQLModel):
    amount: Decimal = Field(sa_column=Column(Numeric(10, 2), nullable=False))
    method: PaymentMethod
    status: PaymentStatus = Field(
        sa_column=Column(
            payment_status_enum,
            nullable=False,
            server_default=PaymentStatus.PENDING.value
        )
    )
    order_id: UUID = Field(foreign_key="order.id", index=True)
    transaction_id: Optional[str] = Field(default=None, max_length=100)