from pydantic import BaseModel
from datetime import datetime
from typing import List, Annotated, Optional



class UserCreate(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    user_id: str
    username: str
    created: datetime

class UserDB(BaseModel):
    user_id: str
    username: str
    password: str
    created: datetime

class UserUpdate(BaseModel):
    username: Optional[str] = None
    password: Optional[str] = None