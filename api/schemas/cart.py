from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, Field


class CartItemCreate(BaseModel):
    product_id: UUID
    quantity: int = Field(1, ge=1, description="Количество товара")


class CartItemUpdate(BaseModel):
    quantity: int = Field(..., ge=0, description="Новое количество (0 = удалить)")


class CartItemShow(BaseModel):
    product_id: UUID
    quantity: int
    subtotal: float
    product_name: Optional[str] = None
    product_price: Optional[float] = None
    product_discount: Optional[float] = None

    class Config:
        from_attributes = True


class CartShow(BaseModel):
    cart_id: UUID
    total_price: float
    items: List[CartItemShow]
    items_count: int

    class Config:
        from_attributes = True