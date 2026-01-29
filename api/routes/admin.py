from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from typing import List

from api.schemas.product import ProductCreate, ProductUpdate, ProductShow
from api.schemas.category import CategoryCreate, CategoryUpdate, CategoryShow
from api.dependencies.auth import require_admin
from db.dals.admin_dal import AdminDAL
from db.session import get_db

router = APIRouter(prefix="/admin", tags=["admin"])


# Product 

@router.post("/products/", response_model=ProductShow, status_code=201)
async def create_product(
    data: ProductCreate,
    admin = Depends(require_admin),
    session: AsyncSession = Depends(get_db)
):
    dal = AdminDAL(session)
    product = await dal.create_product(**data.dict())
    await session.commit()
    await session.refresh(product)
    return product


@router.get("/products/{product_id}", response_model=ProductShow)
async def get_product(
    product_id: UUID,
    admin = Depends(require_admin),
    session: AsyncSession = Depends(get_db)
):
    dal = AdminDAL(session)
    product = await dal.get_product_by_id(product_id)
    if not product:
        raise HTTPException(404, "Товар не найден")
    return product


@router.patch("/products/{product_id}", response_model=ProductShow)
async def update_product(
    product_id: UUID,
    data: ProductUpdate,
    admin = Depends(require_admin),
    session: AsyncSession = Depends(get_db)
):
    dal = AdminDAL(session)
    updated_id = await dal.update_product(product_id, **data.dict(exclude_unset=True))
    if not updated_id:
        raise HTTPException(404, "Товар не найден")
    product = await dal.get_product_by_id(product_id)
    return product


@router.delete("/products/{product_id}", status_code=204)
async def delete_product(
    product_id: UUID,
    admin = Depends(require_admin),
    session: AsyncSession = Depends(get_db)
):
    dal = AdminDAL(session)
    deleted_id = await dal.delete_product(product_id)
    if not deleted_id:
        raise HTTPException(404, "Товар не найден")


# Category 

@router.post("/categories/", response_model=CategoryShow, status_code=201)
async def create_category(
    data: CategoryCreate,
    admin = Depends(require_admin),
    session: AsyncSession = Depends(get_db)
):
    dal = AdminDAL(session)
    category = await dal.create_category(**data.dict())
    await session.commit()
    await session.refresh(category)
    return category


@router.patch("/categories/{category_id}", response_model=CategoryShow)
async def update_category(
    category_id: UUID,
    data: CategoryUpdate,
    admin = Depends(require_admin),
    session: AsyncSession = Depends(get_db)
):
    dal = AdminDAL(session)
    updated_id = await dal.update_category(category_id, **data.dict(exclude_unset=True))
    if not updated_id:
        raise HTTPException(404, "Категория не найдена")
    category = await dal.get_category_by_id(category_id)
    return category


@router.delete("/categories/{category_id}", status_code=204)
async def delete_category(
    category_id: UUID,
    admin = Depends(require_admin),
    session: AsyncSession = Depends(get_db)
):
    dal = AdminDAL(session)
    deleted_id = await dal.delete_category(category_id)
    if not deleted_id:
        raise HTTPException(404, "Категория не найдена")