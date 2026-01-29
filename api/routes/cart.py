from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.schemas import user
from api.schemas.cart import CartShow, CartItemCreate, CartItemUpdate, CartItemShow
from api.dependencies.auth import get_current_user
from api.dependencies.cart import get_user_cart   
from db.dals.cart_dal import CartDAL
from db.models import Cart, User
from db.session import get_db

router = APIRouter(prefix="/cart", tags=["cart"])


@router.get("/", response_model=CartShow)
async def get_cart(
    cart: Cart = Depends(get_user_cart)
):
    items_show = []
    for item in cart.items:
        p = item.product
        items_show.append(CartItemShow(
            product_id=item.product_id,
            quantity=item.quantity,
            subtotal=item.subtotal,
            product_name=getattr(p, "name", None),
            product_price=getattr(p, "price", None),
            product_discount=getattr(p, "discount_percentage", None),
        ))

    return CartShow(
        cart_id=cart.cart_id,
        total_price=cart.total_price,
        items=items_show,
        items_count=len(cart.items)
    )


@router.post("/items/", response_model=CartShow, status_code=201)
async def add_to_cart(
    item_data: CartItemCreate,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
):
    dal = CartDAL(session)
    cart = await dal.get_or_create_cart(user)
    await dal.add_item(cart, item_data.product_id, item_data.quantity)
    await session.commit()
    cart = await dal.get_or_create_cart(user)
    return await get_cart(cart=cart)  


@router.patch("/items/{product_id}", response_model=CartShow)
async def update_cart_item(
    product_id: UUID,
    data: CartItemUpdate,
    cart: Cart = Depends(get_user_cart),
    session: AsyncSession = Depends(get_db)
):
    dal = CartDAL(session)
    updated = await dal.update_item_quantity(cart.cart_id, product_id, data.quantity)
    if not updated and data.quantity > 0:
        raise HTTPException(404, "Товар не найден в корзине")
    await session.commit()
    cart = await dal.get_or_create_cart(user)
    return await get_cart(cart=cart)


@router.delete("/items/{product_id}", status_code=204)
async def remove_from_cart(
    product_id: UUID,
    cart: Cart = Depends(get_user_cart),
    session: AsyncSession = Depends(get_db)
):
    dal = CartDAL(session)
    removed = await dal.remove_item(cart.cart_id, product_id)
    if not removed:
        raise HTTPException(404, "Товар не найден в корзине")
    await session.commit()


@router.delete("/", status_code=204)
async def clear_cart(
    cart: Cart = Depends(get_user_cart),
    session: AsyncSession = Depends(get_db)
):
    dal = CartDAL(session)
    await dal.clear_cart(cart.cart_id)
    await session.commit()