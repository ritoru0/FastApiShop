from uuid import UUID
from typing import List
from datetime import datetime
from pydantic import BaseModel


class OrderItemShow(BaseModel):
    product_id: UUID
    quantity: int
    price: float

    class Config:
        from_attributes = True


class OrderShow(BaseModel):
    order_id: UUID
    user_id: UUID
    total: float
    status: float
    created_at: datetime
    items: List[OrderItemShow]

    class Config:
        from_attributes = True