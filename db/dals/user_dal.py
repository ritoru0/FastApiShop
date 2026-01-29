from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import User


class UserDAL:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_user(
        self,
        name: str,
        surname: str,
        email: str,
        password_hash: str,
    ) -> User:
       
        query = select(User).where(User.email == email)
        result = await self.session.execute(query)
        if result.scalar_one_or_none():
            raise ValueError("Пользователь с таким email уже существует")

        new_user = User(
            name=name,
            surname=surname,
            email=email,
            password_hash=password_hash,
            role=["user"],
        )

        self.session.add(new_user)
        await self.session.commit()
        await self.session.refresh(new_user)

        return new_user

    async def get_user_by_email(self, email: str) -> Optional[User]:
        
        query = select(User).where(User.email == email)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()