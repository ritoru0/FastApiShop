import re
from uuid import UUID

from pydantic import BaseModel, Field, validator

CATEGORY_NAME_PATTERN = re.compile(r"^[а-яА-Яa-zA-Z\s\-]+$")


class CategoryCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    description: str | None = Field(None, max_length=1000)

    @validator("name")
    def validate_name(cls, value: str):
        value = value.strip()
        if not CATEGORY_NAME_PATTERN.match(value):
            raise ValueError("Название категории должно содержать только буквы, пробелы и дефис")
        return value.title()


class CategoryUpdate(BaseModel):
    name: str | None = Field(None, min_length=2, max_length=100)
    description: str | None = Field(None, max_length=1000)

    @validator("name")
    def validate_name_update(cls, value: str | None):
        if value is not None:
            value = value.strip()
            if not CATEGORY_NAME_PATTERN.match(value):
                raise ValueError("Название категории должно содержать только буквы, пробелы и дефис")
            return value.title()
        return value


class CategoryShow(BaseModel):
    category_id: UUID
    name: str
    description: str | None

    class Config:
        from_attributes = True