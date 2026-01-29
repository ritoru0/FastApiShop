from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from uuid import UUID

from api.schemas.product import ProductShow, ProductListResponse
from db.session import get_db
from db.models import Product, Category
from sqlalchemy import select, func

router = APIRouter(prefix="/products", tags=["public_products"])


@router.get("/", response_model=ProductListResponse)
async def get_products_list(
    session: AsyncSession = Depends(get_db),
    
    page: int = Query(1, ge=1, description="Номер страницы"),
    size: int = Query(20, ge=1, le=100, description="Количество товаров на странице"),
    
    category_id: Optional[UUID] = Query(None, description="ID категории"),
    search: Optional[str] = Query(None, description="Поиск по названию (частичное совпадение)"),
    
    sort: str = Query(
        "name_asc",
        description="Варианты: name_asc, name_desc, price_asc, price_desc, newest, discount_desc"
    ),
):
    offset = (page - 1) * size

    stmt = select(Product)

    if category_id:
        stmt = stmt.where(Product.category_id == category_id)

    if search:
        stmt = stmt.where(Product.name.ilike(f"%{search}%"))

    match sort:
        case "name_asc":
            stmt = stmt.order_by(Product.name.asc())
        case "name_desc":
            stmt = stmt.order_by(Product.name.desc())
        case "price_asc":
            stmt = stmt.order_by(Product.price.asc())
        case "price_desc":
            stmt = stmt.order_by(Product.price.desc())
        case "newest":
            stmt = stmt.order_by(Product.product_id.desc())  
        case "discount_desc":
            stmt = stmt.order_by(Product.discount_percentage.desc())
        case _:
            stmt = stmt.order_by(Product.name.asc())

    count_stmt = select(func.count()).select_from(stmt.subquery())
    total_result = await session.execute(count_stmt)
    total = total_result.scalar_one()

    stmt = stmt.offset(offset).limit(size)
    result = await session.execute(stmt)
    products = result.scalars().all()

    if not products and page > 1:
        raise HTTPException(404, "Страница не найдена")

    return {
        "items": products,
        "total": total,
        "page": page,
        "size": size,
        "pages": (total + size - 1) // size if total > 0 else 0
    }


@router.get("/{product_id}", response_model=ProductShow)
async def get_product_detail(
    product_id: UUID,
    session: AsyncSession = Depends(get_db)
):
    stmt = select(Product).where(Product.product_id == product_id)
    result = await session.execute(stmt)
    product = result.scalars().first()

    if not product:
        raise HTTPException(status_code=404, detail="Товар не найден")

    return product