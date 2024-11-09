from typing import Optional

from pydantic import BaseModel

class UserResponse(BaseModel):
    status_code: int
    message: str
    transaction: dict

class UpdateUser (BaseModel):
    role: Optional[str] = 'client'
    is_admin: Optional[bool] = False

class CreateUser(BaseModel):
    name: str
    email: str
    password: str

class ViewsUser(BaseModel):
    id: int
    name: str
    email: str



