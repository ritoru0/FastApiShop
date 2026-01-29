from fastapi import Depends, HTTPException, status

from api.dependencies.auth import get_current_user
from db.dals.cart_dal import CartDAL
from db.models import User, Cart
from db.session import get_db
from sqlalchemy.ext.asyncio import AsyncSession


async def get_user_cart(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
) -> Cart:
    dal = CartDAL(session)
    cart = await dal.get_or_create_cart(current_user)
    return cart