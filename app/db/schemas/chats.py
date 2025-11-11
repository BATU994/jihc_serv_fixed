from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional
class Message(BaseModel):
    chat_id:int
    id:int
    sender_id: int
    receiver_id: int
    content: str
    timestamp: datetime


class MessagePost(BaseModel):
    sender_id: int
    receiver_id: int
    content: str
    

class Chat(BaseModel):
    id: int
    user_ids: List[int]
    user_names: List[str]
    last_message: Optional[str]
    item: str
    item_image: str
    item_id: str
    created_at: datetime

    class Config:
        orm_mode = True