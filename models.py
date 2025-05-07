from typing import Optional, Annotated, List
from pydantic import BaseModel, Field, BeforeValidator, field_validator

# Custom type for ObjectId strings (e.g., MongoDB)
PyObjectId = Annotated[str, BeforeValidator(str)]

# Car Models
class CarModel(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    brand: str = Field(...)
    make: str = Field(...)
    year: int = Field(..., gt=1970, lt=2025)
    cm3: int = Field(..., gt=0, lt=5000)
    km: int = Field(..., gt=0, lt=500 * 1000)
    price: int = Field(..., gt=0, lt=100000)
    user_id: str = Field(...)
    picture_url: Optional[str] = Field(None)

    @field_validator("brand", mode="before")
    @classmethod
    def check_brand_case(cls, v: str) -> str:
        print(f"check_brand_case called with: '{v}'")
        return v.title()

    @field_validator("make", mode="before")
    @classmethod
    def check_make_case(cls, v: str) -> str:
        print(f"check_make_case called with: '{v}'")
        return v.title()

class UpdateCarModel(BaseModel):
    brand: Optional[str] = Field(None)
    make: Optional[str] = Field(None)
    year: Optional[int] = Field(None, gt=1970, lt=2025)
    cm3: Optional[int] = Field(None, gt=0, lt=5000)
    km: Optional[int] = Field(None, gt=0, lt=500 * 1000)
    price: Optional[int] = Field(None, gt=0, lt=100 * 1000)

class CarCollection(BaseModel):
    cars: List[CarModel]

class CarCollectionPagination(CarCollection):
    page: int = Field(ge=1, default=1)
    has_more: bool

# User Models
class UserModel(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    username: str = Field(..., min_length=3, max_length=15)
    password: str = Field(...)

class LoginModel(BaseModel):
    username: str = Field(...)
    password: str = Field(...)

class CurrentUserModel(BaseModel):
    id: PyObjectId = Field(alias="_id", default=None)
    username: str = Field(..., min_length=3, max_length=15)
