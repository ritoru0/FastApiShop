from typing import Union, List, Optional
from uuid import UUID

from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import Product, Category


class AdminDAL:
    
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    # Product 

    async def create_product(
        self,
        name: str,
        price: float,
        category_id: UUID,
        description: Optional[str] = None,
        stock: int = 0,
        discount_percentage: float = 0.0,
        images: List[str] = None,
    ) -> Product:
        new_product = Product(
            name=name,
            price=price,
            description=description,
            stock=stock,
            discount_percentage=discount_percentage,
            category_id=category_id,
            images=images or [],
        )
        self.db_session.add(new_product)
        await self.db_session.flush()
        return new_product

    async def get_product_by_id(self, product_id: UUID) -> Union[Product, None]:
        query = select(Product).where(Product.product_id == product_id)
        res = await self.db_session.execute(query)
        row = res.fetchone()
        if row:
            return row[0]
        return None

    async def update_product(self, product_id: UUID, **kwargs) -> Union[UUID, None]:
        if not kwargs:
            return None

        query = (
            update(Product)
            .where(Product.product_id == product_id)
            .values(**kwargs)
            .returning(Product.product_id)
        )
        res = await self.db_session.execute(query)
        row = res.fetchone()
        if row:
            return row[0]
        return None

    async def delete_product(self, product_id: UUID) -> Union[UUID, None]:
        query = (
            delete(Product)
            .where(Product.product_id == product_id)
            .returning(Product.product_id)
        )
        res = await self.db_session.execute(query)
        row = res.fetchone()
        if row:
            return row[0]
        return None

    # Category

    async def create_category(
        self,
        name: str,
        description: Optional[str] = None,
    ) -> Category:
        new_category = Category(
            name=name,
            description=description,
        )
        self.db_session.add(new_category)
        await self.db_session.flush()
        return new_category

    async def get_category_by_id(self, category_id: UUID) -> Union[Category, None]:
        query = select(Category).where(Category.category_id == category_id)
        res = await self.db_session.execute(query)
        row = res.fetchone()
        if row:
            return row[0]
        return None

    async def update_category(self, category_id: UUID, **kwargs) -> Union[UUID, None]:
        if not kwargs:
            return None

        query = (
            update(Category)
            .where(Category.category_id == category_id)
            .values(**kwargs)
            .returning(Category.category_id)
        )
        res = await self.db_session.execute(query)
        row = res.fetchone()
        if row:
            return row[0]
        return None

    async def delete_category(self, category_id: UUID) -> Union[UUID, None]:
        query = (
            delete(Category)
            .where(Category.category_id == category_id)
            .returning(Category.category_id)
        )
        res = await self.db_session.execute(query)
        row = res.fetchone()
        if row:
            return row[0]
        return None