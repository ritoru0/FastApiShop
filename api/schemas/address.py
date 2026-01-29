from uuid import UUID
from typing import Optional
from pydantic import BaseModel, Field, field_validator, model_validator
import re

CITY_STREET_PATTERN = re.compile(r'^[а-яА-ЯёЁa-zA-Z0-9\s\-.,/()№"]+$')
HOUSE_PATTERN = re.compile(r'^[\d/а-яА-ЯёЁa-zA-Z\-]+$')
APARTMENT_PATTERN = re.compile(r'^[\dа-яА-ЯёЁa-zA-Z\-/]+$')
POSTAL_CODE_PATTERN = re.compile(r'^\d{5}(-\d{4})?$')


class AddressCreate(BaseModel):
    city: str = Field(..., min_length=2, max_length=100, description="Город / населённый пункт")
    street: str = Field(..., min_length=2, max_length=200, description="Улица")
    house: str = Field(..., min_length=1, max_length=20, description="Дом / строение")
    apartment: Optional[str] = Field(None, max_length=20, description="Квартира / офис")
    postal_code: Optional[str] = Field(None, max_length=20, description="Почтовый индекс")
    is_default: bool = Field(default=False, description="Сделать адресом по умолчанию")

    @field_validator("city", "street")
    @classmethod
    def validate_city_street(cls, v: str) -> str:
        v = v.strip()
        if not CITY_STREET_PATTERN.match(v):
            raise ValueError("Допустимы буквы, цифры, пробелы, дефисы, точки, запятые, слэши, кавычки")
        return v.title()

    @field_validator("house")
    @classmethod
    def validate_house(cls, v: str) -> str:
        v = v.strip()
        if not HOUSE_PATTERN.match(v):
            raise ValueError("Номер дома может содержать цифры, буквы, дефис, слэш")
        return v.upper()

    @field_validator("apartment")
    @classmethod
    def validate_apartment(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        v = v.strip()
        if v and not APARTMENT_PATTERN.match(v):
            raise ValueError("Номер квартиры/офиса может содержать цифры, буквы, дефис, слэш")
        return v.upper()

    @field_validator("postal_code")
    @classmethod
    def validate_postal_code(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        v = v.strip()
        if v and not POSTAL_CODE_PATTERN.match(v):
            raise ValueError("Почтовый индекс должен соответствовать формату (5 цифр или 5-4)")
        return v

    @model_validator(mode="after")
    def check_required_fields_together(self):
        if not self.city or not self.street or not self.house:
            raise ValueError("Город, улица и номер дома — обязательные поля")
        return self


class AddressUpdate(BaseModel):
    city: Optional[str] = Field(None, min_length=2, max_length=100)
    street: Optional[str] = Field(None, min_length=2, max_length=200)
    house: Optional[str] = Field(None, min_length=1, max_length=20)
    apartment: Optional[str] = Field(None, max_length=20)
    postal_code: Optional[str] = Field(None, max_length=20)
    is_default: Optional[bool] = None

    @field_validator("city", "street")
    @classmethod
    def validate_city_street_update(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        v = v.strip()
        if not CITY_STREET_PATTERN.match(v):
            raise ValueError("Допустимы буквы, цифры, пробелы, дефисы, точки, запятые, слэши, кавычки")
        return v.title()

    @field_validator("house")
    @classmethod
    def validate_house_update(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        v = v.strip()
        if not HOUSE_PATTERN.match(v):
            raise ValueError("Номер дома может содержать цифры, буквы, дефис, слэш")
        return v.upper()

class AddressShow(BaseModel):
    address_id: UUID
    city: str
    street: str
    house: str
    apartment: Optional[str] = None
    postal_code: Optional[str] = None
    is_default: bool

    class Config:
        from_attributes = True