from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from uuid import UUID

from api.schemas.order import OrderShow
from api.dependencies.auth import get_current_user
from api.dependencies.cart import get_user_cart
from db.dals.order_dal import OrderDAL
from db.dals.cart_dal import CartDAL
from db.models import User, Cart
from db.session import get_db

router = APIRouter(prefix="/orders", tags=["orders"])


@router.post("/", response_model=OrderShow, status_code=201)
async def create_order(
    user: User = Depends(get_current_user),
    cart: Cart = Depends(get_user_cart),
    session: AsyncSession = Depends(get_db)
):
    if not cart.items:
        raise HTTPException(status_code=400, detail="Корзина пуста")

    order_dal = OrderDAL(session)
    cart_dal = CartDAL(session)

    order = await order_dal.create_order_from_cart(cart, user.user_id)

    await session.commit()

    await cart_dal.clear_cart(cart.cart_id)
    await session.commit()

    order = await order_dal.get_order_by_id(order.order_id, user.user_id)
    if not order:
        raise HTTPException(status_code=500, detail="Ошибка при создании заказа")

    return order


@router.get("/", response_model=List[OrderShow])
async def get_my_orders(
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
):
    dal = OrderDAL(session)
    orders = await dal.get_user_orders(user.user_id)
    return orders


@router.get("/{order_id}", response_model=OrderShow)
async def get_order_detail(
    order_id: UUID,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
):
    dal = OrderDAL(session)
    order = await dal.get_order_by_id(order_id, user.user_id)
    if not order:
        raise HTTPException(status_code=404, detail="Заказ не найден или не принадлежит вам")
    return order