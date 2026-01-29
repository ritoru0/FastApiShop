from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm


from sqlalchemy.ext.asyncio import AsyncSession
from db.session import get_db                 

from api.schemas.auth import Token
from api.dependencies.auth import authenticate_user
from core.security import create_access_token
from db.models import User

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/token", response_model=Token)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: Annotated[AsyncSession, Depends(get_db)]
):
    user: User | None = await authenticate_user(
        email=form_data.username,
        password=form_data.password,
        session=session
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный имайл или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(
        data={"sub": user.email, "roles": user.role}
    )

    return {"access_token": access_token, "token_type": "bearer"}