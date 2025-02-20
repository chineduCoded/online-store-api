from sqlmodel import Field, Relationship, Column, UUID as SQLModelUUID, text, ForeignKey
from datetime import datetime
from uuid import UUID
from typing import Optional, TYPE_CHECKING
from app.utils.datetime_now import datetime_now
from app.schemas.payment_schema import PaymentBase, PaymentStatus, PaymentMethod

if TYPE_CHECKING:
    from app.models import Order

class Payment(PaymentBase, table=True):
    id: Optional[UUID] = Field(
        default=None,
        sa_column=Column(
            SQLModelUUID(as_uuid=True),
            primary_key=True,
            server_default=text("gen_random_uuid()")
        )
    )
    created_at: datetime = Field(default_factory=datetime_now)
    updated_at: datetime = Field(default_factory=datetime_now)

    order: "Order" = Relationship(back_populates="payments")
    order_id: UUID = Field(
        sa_column=Column(
            SQLModelUUID(as_uuid=True),
            ForeignKey("order.id", ondelete="CASCADE")
        ) # Cascade deletes the payment when the order is deleted
    )

    def update_status(self, status: PaymentStatus):
        self.status = status
        self.updated_at = datetime_now()

    @property
    def is_successful(self) -> bool:
        return self.status in [PaymentStatus.SUCCESS, PaymentStatus.REFUNDED]

    @property
    def is_refundable(self) -> bool:
        return self.status == PaymentStatus.SUCCESS

    @property
    def payment_method_icon(self) -> str:
        return "credit-card" if self.method == PaymentMethod.CREDIT_CARD else "cash"
