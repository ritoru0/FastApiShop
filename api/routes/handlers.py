from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.schemas.user import UserCreate, ShowUser
from api.dependencies.auth import get_current_user
from core.hashing import get_password_hash
from db.dals.user_dal import UserDAL
from db.session import get_db
from db.models import User

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", response_model=ShowUser, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: UserCreate,
    session: AsyncSession = Depends(get_db)
):
   
    dal = UserDAL(session)

    try:
        hashed_password = get_password_hash(user_data.password)
        new_user = await dal.create_user(
            name=user_data.name,
            surname=user_data.surname,
            email=user_data.email,
            password_hash=hashed_password,
        )
        return ShowUser.model_validate(new_user)

    except ValueError as e:
       
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Внутренняя ошибка сервера: {str(e)}"
        )


@router.get("/me", response_model=ShowUser)
async def get_current_user_profile(
    current_user: User = Depends(get_current_user)
):
    
    return ShowUser.model_validate(current_user)