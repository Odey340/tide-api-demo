from pydantic import BaseModel, EmailStr
from datetime import datetime

# -------- USER SCHEMAS --------

class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserCreate(UserBase):
    password: str  # if you handle passwords on API side

class User(UserBase):
    id: int

    class Config:
        from_attributes = True  # replaces orm_mode


# -------- TIDE SCHEMAS --------

class TideBase(BaseModel):
    location: str
    date: datetime
    height: float

class TideCreate(TideBase):
    pass

class Tide(TideBase):
    id: int

    class Config:
        from_attributes = True

        from pydantic import BaseModel
from datetime import datetime

class Tide(BaseModel):
    id: int
    city: str
    height: float
    time: datetime

    class Config:
        orm_mode = True