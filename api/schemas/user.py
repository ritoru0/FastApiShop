import re
from typing import List
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, validator

LETTER_MATCH_PATTERN = re.compile(r"^[а-яА-Яa-zA-Z\-]+$")


class UserCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    surname: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=8)

    @validator("name")
    def validate_name(cls, value: str):
        value = value.strip()
        if not LETTER_MATCH_PATTERN.match(value):
            raise ValueError("Name should contain only letters and hyphen")
        return value.title()

    @validator("surname")
    def validate_surname(cls, value: str):
        value = value.strip()
        if not LETTER_MATCH_PATTERN.match(value):
            raise ValueError("Surname should contain only letters and hyphen")
        return value.title()


class ShowUser(BaseModel):
    user_id: UUID
    name: str
    surname: str
    email: EmailStr
    role: List[str]

    class Config:
        from_attributes = True