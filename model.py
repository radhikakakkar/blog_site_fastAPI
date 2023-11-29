from pydantic import BaseModel
from typing import Optional

class Blog(BaseModel):
    title : str
    nickname : str
    media : str
    description : str
    snippet : Optional[str] = None

class UserSchema(BaseModel):
    full_name: str
    email: str
    password: str

class UserLoginSchema(BaseModel):
    email: str
    password: str

class BlogUpdate(Blog):
    title : Optional[str] = None
    nickname : Optional[str] = None
    media : Optional[str] = None
    description : Optional[str] = None
    snippet : Optional[str] = None