from pydantic import BaseModel
from typing import Optional

class LostAndFoundBase(BaseModel):
    userId: int
    item_name: str
    isLost: bool
    desc: str
    date: str
    location: str
    image: Optional[str]  # file path or URL
    isResolved: bool = False

class LostAndFoundCreate(LostAndFoundBase):
    pass

class LostAndFound(LostAndFoundBase):
    id: int
    item_id: str
    class Config:
        orm_mode = True
