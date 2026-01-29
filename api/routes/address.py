from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from uuid import UUID

from api.schemas.address import AddressCreate, AddressUpdate, AddressShow
from api.dependencies.auth import get_current_user
from db.dals.address_dal import AddressDAL
from db.models import User
from db.session import get_db

router = APIRouter(prefix="/addresses", tags=["addresses"])


@router.post("/", response_model=AddressShow, status_code=201)
async def create_address(
    data: AddressCreate,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
):
    dal = AddressDAL(session)
    address = await dal.create_address(user, data.model_dump(exclude_unset=True))
    await session.commit()
    await session.refresh(address)
    return address


@router.get("/", response_model=List[AddressShow])
async def get_my_addresses(
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
):
    dal = AddressDAL(session)
    addresses = await dal.get_user_addresses(user.user_id)
    return addresses


@router.get("/{address_id}", response_model=AddressShow)
async def get_address(
    address_id: UUID,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
):
    dal = AddressDAL(session)
    address = await dal.get_address_by_id(address_id, user.user_id)
    if not address:
        raise HTTPException(status_code=404, detail="Адрес не найден")
    return address


@router.patch("/{address_id}", response_model=AddressShow)
async def update_address(
    address_id: UUID,
    data: AddressUpdate,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
):
    dal = AddressDAL(session)
    address = await dal.get_address_by_id(address_id, user.user_id)
    if not address:
        raise HTTPException(status_code=404, detail="Адрес не найден")

    updated_data = data.model_dump(exclude_unset=True)
    if "is_default" in updated_data and updated_data["is_default"]:
        await dal.set_default_address(address_id, user.user_id)

    address = await dal.update_address(address, updated_data)
    await session.commit()
    await session.refresh(address)
    return address


@router.delete("/{address_id}", status_code=204)
async def delete_address(
    address_id: UUID,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
):
    dal = AddressDAL(session)
    deleted = await dal.delete_address(address_id, user.user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Адрес не найден")
    await session.commit()