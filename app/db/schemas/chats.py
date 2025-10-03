from pydantic import BaseModel, field_validator
from pydantic import ConfigDict
from typing import List, Optional
from datetime import datetime

class Message(BaseModel):
    id: int
    sender_id: int
    receiver_id: int
    content: str
    timestamp: datetime
    model_config = ConfigDict(from_attributes=True)

class MessageCreate(BaseModel):
    content: str

class Chat(BaseModel):
    id: int
    user_ids: List[int]
    user_names: List[str]
    last_message: Optional[str] = None
    item: Optional[str] = None
    item_image: Optional[str] = None
    item_id: Optional[str] = None
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
    @field_validator("user_ids", mode="before")
    @classmethod
    def coerce_user_ids(cls, v):
        if isinstance(v, str):
            return [int(x) for x in v.split(",") if x.strip() != ""]
        return v
    @field_validator("user_names", mode="before")
    @classmethod
    def coerce_user_names(cls, v):
        if isinstance(v, str):
            return [x for x in v.split(",") if x.strip() != ""]
        return v

class ChatCreate(BaseModel):
    user_ids: List[int]
    user_names: List[str]
    item: Optional[str] = None
    item_image: Optional[str] = None
    item_id: Optional[str] = None
    @field_validator("user_ids")
    @classmethod
    def validate_user_ids(cls, v):
        if not isinstance(v, list) or len(v) != 2:
            raise ValueError("user_ids must contain exactly two user ids")
        try:
            ids = [int(x) for x in v]
        except Exception:
            raise ValueError("user_ids must be integers")
        if ids[0] == ids[1]:
            raise ValueError("user_ids must be two distinct user ids")
        return ids
    @field_validator("user_names")
    @classmethod
    def validate_user_names(cls, v):
        if not isinstance(v, list) or len(v) != 2:
            raise ValueError("user_names must contain exactly two names")
        for name in v:
            if not isinstance(name, str) or name.strip() == "":
                raise ValueError("user_names must be non-empty strings")
        return [name.strip() for name in v]