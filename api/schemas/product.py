import re
from typing import List
from uuid import UUID

from pydantic import BaseModel, Field, validator

PRODUCT_NAME_PATTERN = re.compile(r"^[а-яА-Яa-zA-Z0-9\s\-]+$")


class ProductCreate(BaseModel):
    name: str = Field(..., min_length=3, max_length=200)
    price: float = Field(..., gt=0)
    description: str | None = Field(None, max_length=2000)
    stock: int = Field(..., ge=0)
    discount_percentage: float = Field(0.0, ge=0, le=100)
    category_id: UUID
    images: List[str] = Field(default_factory=list)

    @validator("name")
    def validate_name(cls, value: str):
        value = value.strip()
        if not PRODUCT_NAME_PATTERN.match(value):
            raise ValueError("Название товара должно содержать только буквы, цифры, пробелы и дефис")
        return value.title()


class ProductUpdate(BaseModel):
    name: str | None = Field(None, min_length=3, max_length=200)
    price: float | None = Field(None, gt=0)
    description: str | None = Field(None, max_length=2000)
    stock: int | None = Field(None, ge=0)
    discount_percentage: float | None = Field(None, ge=0, le=100)
    category_id: UUID | None = None
    images: List[str] | None = None

    @validator("name")
    def validate_name_update(cls, value: str | None):
        if value is not None:
            value = value.strip()
            if not PRODUCT_NAME_PATTERN.match(value):
                raise ValueError("Название товара должно содержать только буквы, цифры, пробелы и дефис")
            return value.title()
        return value


class ProductShow(BaseModel):
    product_id: UUID
    name: str
    price: float
    description: str | None
    stock: int
    discount_percentage: float
    category_id: UUID
    images: List[str]

    class Config:
        from_attributes = True
        
class ProductListResponse(BaseModel):
    items: List[ProductShow]
    total: int
    page: int
    size: int
    pages: int