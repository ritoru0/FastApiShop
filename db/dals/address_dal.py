from typing import List, Optional
from uuid import UUID

from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import Address, User


class AddressDAL:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_address(self, user: User, data: dict) -> Address:
        address = Address(user_id=user.user_id, **data)
        self.session.add(address)
        await self.session.flush()
        return address

    async def get_user_addresses(self, user_id: UUID) -> List[Address]:
        stmt = select(Address).where(Address.user_id == user_id).order_by(Address.is_default.desc(), Address.address_id)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_address_by_id(self, address_id: UUID, user_id: UUID) -> Optional[Address]:
        stmt = select(Address).where(
            Address.address_id == address_id,
            Address.user_id == user_id
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def update_address(self, address: Address, data: dict) -> Address:
        for key, value in data.items():
            if value is not None:
                setattr(address, key, value)
        await self.session.flush()
        return address

    async def delete_address(self, address_id: UUID, user_id: UUID) -> bool:
        stmt = delete(Address).where(
            Address.address_id == address_id,
            Address.user_id == user_id
        )
        result = await self.session.execute(stmt)
        return result.rowcount > 0

    async def set_default_address(self, address_id: UUID, user_id: UUID) -> bool:

        reset_stmt = (
            update(Address)
            .where(Address.user_id == user_id)
            .values(is_default=False)
        )
        await self.session.execute(reset_stmt)

        set_stmt = (
            update(Address)
            .where(
                Address.address_id == address_id,
                Address.user_id == user_id
            )
            .values(is_default=True)
        )
        result = await self.session.execute(set_stmt)
        return result.rowcount > 0