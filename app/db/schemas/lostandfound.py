from pydantic import BaseModel
from typing import Optional

class LostAndFoundBase(BaseModel):
    userId: int
    userName: str
    item_name: str
    isLost: bool
    desc: str
    date: str
    location: str
    image: Optional[str]  # file path or URL
    isResolved: bool = False


class LostAndFoundCreate(LostAndFoundBase):
    pass

class LostAndFoundPartialUpdate(BaseModel):
    userId: Optional[int] = None
    userName: Optional[str] = None
    item_name: Optional[str] = None
    isLost: Optional[bool] = None
    desc: Optional[str] = None
    date: Optional[str] = None
    location: Optional[str] = None
    image: Optional[str] = None  # file path or URL
    isResolved: Optional[bool] = None

class LostAndFound(LostAndFoundBase):
    id: int
    item_id: str
    class Config:
        orm_mode = True
