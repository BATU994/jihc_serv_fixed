from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime
from app.db.sessions import get_async_session
from app.db.schemas import chats as chats_schema
from app.db.models import Chat, Message
from app.deps import get_current_user
import sqlalchemy as sa

router = APIRouter(prefix="/chats", tags=["chats"])

@router.post("/", response_model=chats_schema.Chat)
async def create_chat(
    chat: chats_schema.Chat,
    db: AsyncSession = Depends(get_async_session),
):
    new_chat = Chat(
        user_ids= chat.user_ids,
        user_names=chat.user_names,
        last_message=chat.last_message,
        item=chat.item,
        item_image=chat.item_image,
        item_id=chat.item_id,
        created_at=chat.created_at or datetime.utcnow()
    )
    db.add(new_chat)
    await db.commit()
    await db.refresh(new_chat)
    return new_chat

@router.get("/{user_id}/", response_model=list[chats_schema.Chat])
async def get_chats(
    user_id: int,
    db: AsyncSession = Depends(get_async_session)
):
    result = await db.execute(
        sa.select(Chat).where(
            sa.text(
                "EXISTS (SELECT 1 FROM json_each(chats.user_ids) WHERE value = :uid)"
            )
        ).params(uid=user_id)
    )
    
    return result.scalars().all()





@router.get("/{chat_id}/messages/", response_model=list[chats_schema.Message])
async def get_chat_messages(chat_id: int, db: AsyncSession = Depends(get_async_session)):
    result = await db.execute(
        select(Message).where(Message.chat_id == chat_id).order_by(Message.timestamp.asc())
    )
    return result.scalars().all()
@router.delete("/{chat_id}/")
async def delete_chat(chat_id: int, db: AsyncSession = Depends(get_async_session)):
    result = await db.execute(select(Chat).where(Chat.id == chat_id))
    messages = await db.execute(select(Message).where(Message.chat_id == chat_id))
    for message in messages.scalars().all():
        await db.delete(message)
    chat = result.scalars().first()

    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")

    await db.delete(chat)
    await db.commit()

    return {"message": "Chat deleted successfully"}

active_connections = {}

@router.websocket("/ws/{chat_id}")
async def chat_socket(
    websocket: WebSocket,
    chat_id: int,
    session: AsyncSession = Depends(get_async_session)
):
    await websocket.accept()

    result = await session.execute(
        select(Chat).where(Chat.id == chat_id)
    )
    chat = result.scalar_one_or_none()

    if chat is None:
        await websocket.send_json({"error": "Chat does not exist"})
        await websocket.close()
        return 
    if chat_id not in active_connections:
        active_connections[chat_id] = []
    active_connections[chat_id].append(websocket)

    try:
        while True:
            data = await websocket.receive_json()
            msg_post = chats_schema.MessagePost(**data)

            new_message = Message(
                chat_id=chat_id,
                sender_id=msg_post.sender_id,
                receiver_id=msg_post.receiver_id,
                content=msg_post.content,
            )
            session.add(new_message)
            await session.commit()
            await session.refresh(new_message)

            for ws in list(active_connections[chat_id]):
                try:
                    await ws.send_json({
                        "sender_id": new_message.sender_id,
                        "receiver_id": new_message.receiver_id,
                        "content": new_message.content,
                        "timestamp": new_message.timestamp.isoformat()
                    })
                except RuntimeError:
                    active_connections[chat_id].remove(ws)

    except WebSocketDisconnect:
        active_connections[chat_id].remove(websocket)
        if not active_connections[chat_id]:
            del active_connections[chat_id]
