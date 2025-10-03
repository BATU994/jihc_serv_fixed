from fastapi import APIRouter, Depends, HTTPException
from app.db.schemas.chats import Chat, Message, ChatCreate, MessageCreate
from app.db.sessions import get_async_session
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.db.models import Chat as DBChat, Message as DBMessage
from sqlalchemy import or_, select

router = APIRouter(prefix="/chats", tags=["chats"])

def get_current_user():
    return 1

async def get_chats_for_user(db: AsyncSession, user_id: int):
    uid = str(user_id)
    result = await db.execute(
        select(DBChat).filter(
            or_(
                DBChat.user_ids == uid,
                DBChat.user_ids.like(f"{uid},%"),
                DBChat.user_ids.like(f"%,{uid},%"),
                DBChat.user_ids.like(f"%,{uid}")
            )
        )
    )
    return result.scalars().all()


async def get_messages_for_chat(db: AsyncSession, chat_id: int):
    chat_row = await db.execute(select(DBChat).filter(DBChat.id == chat_id))
    chat = chat_row.scalar_one_or_none()
    if not chat:
        return []
    participants = [int(uid) for uid in chat.user_ids.split(',')]
    if len(participants) != 2:
        return []
    a, b = participants
    result = await db.execute(
        select(DBMessage).filter(
            or_(
                (DBMessage.sender_id == a) & (DBMessage.receiver_id == b),
                (DBMessage.sender_id == b) & (DBMessage.receiver_id == a),
            )
        ).order_by(DBMessage.timestamp)
    )
    return result.scalars().all()


async def create_chat(db: AsyncSession, user_ids: list[int], user_names: list[str], item: str | None, item_image: str | None, item_id: str | None):
    unique_ids = list(dict.fromkeys(user_ids))
    if len(unique_ids) != 2:
        raise ValueError("user_ids must contain exactly two distinct user ids")
    normalized = sorted(unique_ids)
    ids_str = ','.join(map(str, normalized))
    alt_ids_str = ','.join(map(str, reversed(normalized)))
    existing_row = await db.execute(
        select(DBChat).filter(
            or_(
                DBChat.user_ids == ids_str,
                DBChat.user_ids == alt_ids_str
            )
        )
    )
    existing = existing_row.scalar_one_or_none()
    if existing:
        return existing

    if len(user_names) != 2:
        raise ValueError("user_names must contain exactly two names")
    input_id_to_name = {int(uid): name for uid, name in zip(user_ids, user_names)}
    ordered_names = [input_id_to_name[int_id] for int_id in normalized]
    chat = DBChat(
        user_ids=ids_str,
        user_names=','.join(ordered_names),
        last_message=None,
        item=item,
        item_image=item_image,
        item_id=item_id,
    )
    db.add(chat)
    await db.commit()
    await db.refresh(chat)
    return chat


async def send_message(db: AsyncSession, chat_id: int, sender_id: int, content: str):
    # For simplicity, send to all users except sender
    result = await db.execute(select(DBChat).filter(DBChat.id == chat_id))
    chat = result.scalar_one_or_none()
    if not chat:
        return None
    user_ids = [int(uid) for uid in chat.user_ids.split(',') if int(uid) != sender_id]
    messages = []
    for receiver_id in user_ids:
        msg = DBMessage(sender_id=sender_id, receiver_id=receiver_id, content=content)
        db.add(msg)
        messages.append(msg)
    await db.commit()
    for msg in messages:
        await db.refresh(msg)
    return messages[0] if messages else None

@router.get("/", response_model=List[Chat])
@router.get("", response_model=List[Chat])
async def get_chats(db: AsyncSession = Depends(get_async_session), user_id: int = Depends(get_current_user)):
    return await get_chats_for_user(db, user_id)

@router.get("/user/{user_id}", response_model=List[Chat])
@router.get("/user/{user_id}/", response_model=List[Chat])
async def get_chats_by_user(user_id: int, db: AsyncSession = Depends(get_async_session), _: int = Depends(get_current_user)):
    return await get_chats_for_user(db, user_id)

@router.get("/{chat_id}/messages", response_model=List[Message])
@router.get("/{chat_id}/messages/", response_model=List[Message])
async def get_chat_messages(chat_id: int, db: AsyncSession = Depends(get_async_session), user_id: int = Depends(get_current_user)):
    return await get_messages_for_chat(db, chat_id)

@router.post("/{chat_id}/messages", response_model=Message)
@router.post("/{chat_id}/messages/", response_model=Message)
async def send_message_endpoint(chat_id: int, message: MessageCreate, db: AsyncSession = Depends(get_async_session), user_id: int = Depends(get_current_user)):
    msg = await send_message(db, chat_id, user_id, message.content)
    if not msg:
        raise HTTPException(status_code=404, detail="Chat not found or no recipients")
    return msg

@router.post("/", response_model=Chat)
@router.post("", response_model=Chat)
async def create_chat_endpoint(chat: ChatCreate, db: AsyncSession = Depends(get_async_session), user_id: int = Depends(get_current_user)):
    ids = list(dict.fromkeys(chat.user_ids))
    if len(ids) != 2:
        raise HTTPException(status_code=400, detail="user_ids must contain exactly two distinct user ids")
    try:
        chat_obj = await create_chat(db, ids, chat.user_names, chat.item, chat.item_image, chat.item_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return chat_obj
