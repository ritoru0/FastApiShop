from typing import Annotated, Union

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings

from db.dals.user_dal import UserDAL
from db.models import User
from db.session import get_db
from core.hashing import verify_password


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


async def get_user_by_email(
    email: str,
    session: Annotated[AsyncSession, Depends(get_db)]
) -> Union[User, None]:
    
    dal = UserDAL(session)
    return await dal.get_user_by_email(email)


async def authenticate_user(
    email: str,
    password: str,
    session: Annotated[AsyncSession, Depends(get_db)]
) -> Union[User, None]:
    
    user = await get_user_by_email(email, session)
    if not user:
        return None

    if not verify_password(password, user.password_hash):
        return None

    return user


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    session: Annotated[AsyncSession, Depends(get_db)]
) -> User:
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        email: str | None = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError as e:
        raise credentials_exception from e

    user = await get_user_by_email(email, session)
    if user is None:
        raise credentials_exception

    return user

async def require_admin(
    current_user: Annotated[User, Depends(get_current_user)]
) -> User:
    if "admin" not in current_user.role:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступ только для администраторов"
        )
    return current_user