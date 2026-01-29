from typing import List, Optional
from uuid import UUID
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from db.models import Order, OrderItem, Cart


class OrderDAL:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_order_from_cart(self, cart: Cart, user_id: UUID) -> Order:
        if not cart.items:
            raise ValueError("Корзина пуста")

        order = Order(
            user_id=user_id,
            total=Decimal('0'),
            status=1.0
        )
        self.session.add(order)
        await self.session.flush()  

        total = Decimal('0')

        for item in cart.items:
            product = item.product
            if not product:
                continue  

            discount_factor = Decimal('1') - Decimal(str(product.discount_percentage)) / Decimal('100')
            item_total = Decimal(str(item.quantity)) * product.price * discount_factor
            total += item_total

            order_item = OrderItem(
                order_id=order.order_id,
                product_id=product.product_id,
                quantity=item.quantity,
                price=product.price  
            )
            self.session.add(order_item)

        order.total = total
        await self.session.flush()
        return order

    async def get_user_orders(self, user_id: UUID) -> List[Order]:
        stmt = (
            select(Order)
            .where(Order.user_id == user_id)
            .options(selectinload(Order.items))
            .order_by(Order.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_order_by_id(self, order_id: UUID, user_id: UUID) -> Optional[Order]:
        stmt = (
            select(Order)
            .where(Order.order_id == order_id, Order.user_id == user_id)
            .options(selectinload(Order.items))
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()