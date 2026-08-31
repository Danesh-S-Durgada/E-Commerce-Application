from pydantic import BaseModel, Field

class ProductCreate(BaseModel):
    name: str = Field(min_length=2, max_length=150)
    description: str | None = None
    price: float = Field(gt=0)
    image_url: str | None = None
    category: str | None = None
    stock: int = Field(default=0, ge=0)

class ProductResponse(ProductCreate):
    id: int
    model_config = {"from_attributes": True}

class UserCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    email: str
    password: str = Field(min_length=6)

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    role: str
    model_config = {"from_attributes": True}
