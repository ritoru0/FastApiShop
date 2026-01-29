from typing import Optional
from uuid import UUID

from sqlalchemy import select, delete, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from db.models import Cart, CartItem, User


class CartDAL:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_or_create_cart(self, user: User) -> Cart:
        stmt = (
            select(Cart)
            .options(selectinload(Cart.items).selectinload(CartItem.product))
            .where(Cart.user_id == user.user_id)
        )
        result = await self.session.execute(stmt)
        cart = result.scalars().first()

        if cart is None:
            cart = Cart(user_id=user.user_id)
            self.session.add(cart)
            await self.session.flush()

        return cart

    async def add_item(self, cart: Cart, product_id: UUID, quantity: int = 1) -> CartItem:
        stmt = select(CartItem).where(
            CartItem.cart_id == cart.cart_id,
            CartItem.product_id == product_id
        )
        result = await self.session.execute(stmt)
        item = result.scalars().first()

        if item:
            item.quantity += quantity
        else:
            item = CartItem(
                cart_id=cart.cart_id,
                product_id=product_id,
                quantity=quantity
            )
            self.session.add(item)

        await self.session.flush()
        return item

    async def update_item_quantity(
        self,
        cart_id: UUID,
        product_id: UUID,
        quantity: int
    ) -> Optional[CartItem]:
        if quantity == 0:
            await self.remove_item(cart_id, product_id)
            return None

        stmt = (
            update(CartItem)
            .where(CartItem.cart_id == cart_id, CartItem.product_id == product_id)
            .values(quantity=quantity)
            .returning(CartItem)
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def remove_item(self, cart_id: UUID, product_id: UUID) -> bool:
        stmt = delete(CartItem).where(
            CartItem.cart_id == cart_id,
            CartItem.product_id == product_id
        )
        result = await self.session.execute(stmt)
        return result.rowcount > 0

    async def clear_cart(self, cart_id: UUID) -> bool:
        stmt = delete(CartItem).where(CartItem.cart_id == cart_id)
        result = await self.session.execute(stmt)
        return result.rowcount > 0