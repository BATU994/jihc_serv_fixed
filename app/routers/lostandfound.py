from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from app.db import sessions
from app.db.models import LostAndFound
from app.db.schemas import lostandfound as lostandfound_schema
from app.deps import get_current_user

router = APIRouter(
    prefix="/lostandfound",
    tags=["lostandfound"]
)


import os
from fastapi import Form
from uuid import uuid4
from fastapi.responses import FileResponse

@router.post("/", response_model=lostandfound_schema.LostAndFound)
@router.post("", response_model=lostandfound_schema.LostAndFound)
async def create_lostandfound(
    userId: int = Form(...),
    item_name: str = Form(...),
    isLost: bool = Form(...),
    desc: str = Form(...),
    date: str = Form(...),
    location: str = Form(...),
    userName: str = Form(...),
    isResolved: bool = Form(False),
    image: UploadFile = File(None),
    db: AsyncSession = Depends(sessions.get_async_session),
):
    image_path = None
    if image:
        ext = os.path.splitext(image.filename)[1]
        filename = f"{uuid4().hex}{ext}"
        save_dir = os.path.join(os.path.dirname(__file__), "..", "static", "lostandfound")
        save_dir = os.path.abspath(save_dir)
        os.makedirs(save_dir, exist_ok=True)
        file_path = os.path.join(save_dir, filename)
        with open(file_path, "wb") as f:
            f.write(await image.read())
        image_path = f"/static/lostandfound/{filename}"
    item = LostAndFound(
        userId=userId,
        userName=userName,
        item_name=item_name,
        isLost=isLost,
        desc=desc,
        date=date,
        location=location,
        isResolved=isResolved,
        image=image_path,
    )
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item

@router.get("/", response_model=list[lostandfound_schema.LostAndFound])
async def get_all_lostandfound(db: AsyncSession = Depends(sessions.get_async_session)):
    result = await db.execute(select(LostAndFound).filter(LostAndFound.isResolved == False))
    return result.scalars().all()


@router.get("", response_model=list[lostandfound_schema.LostAndFound])
async def get_all_lostandfound_no_slash(db: AsyncSession = Depends(sessions.get_async_session)):
    return await get_all_lostandfound(db)

@router.get("/{item_id}", response_model=lostandfound_schema.LostAndFound)
async def get_lostandfound(item_id: str, db: AsyncSession = Depends(sessions.get_async_session)):
    result = await db.execute(select(LostAndFound).filter(LostAndFound.item_id == item_id))
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

@router.put("/{item_id}", response_model=lostandfound_schema.LostAndFound)
async def update_lostandfound(
    item_id: str,
    updated_item: lostandfound_schema.LostAndFoundBase,
    db: AsyncSession = Depends(sessions.get_async_session),
):
    result = await db.execute(select(LostAndFound).filter(LostAndFound.item_id == item_id))
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    data = updated_item.model_dump(exclude_unset=True)
    data.pop("item_id", None)
    for key, value in data.items():
        setattr(item, key, value)
    await db.commit()
    await db.refresh(item)
    return item

@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_lostandfound(item_id: str, db: AsyncSession = Depends(sessions.get_async_session)):
    result = await db.execute(select(LostAndFound).filter(LostAndFound.item_id == item_id))
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    await db.delete(item)
    await db.commit()
    return None

@router.patch("/{item_id}", response_model=lostandfound_schema.LostAndFound)
async def patch_lostandfound(
    item_id: str,
    updates: lostandfound_schema.LostAndFoundPartialUpdate,
    db: AsyncSession = Depends(sessions.get_async_session),
):
    result = await db.execute(select(LostAndFound).filter(LostAndFound.item_id == item_id))
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    data = updates.model_dump(exclude_unset=True, exclude_none=True)
    if not data:
        raise HTTPException(status_code=400, detail="No fields provided to update")
    for key, value in data.items():
        if hasattr(item, key):
            setattr(item, key, value)
    await db.commit()
    await db.refresh(item)
    return item

@router.get("/user/{userId}", response_model=list[lostandfound_schema.LostAndFound])
async def get_users_items(
    userId: int,
    db: AsyncSession = Depends(sessions.get_async_session),
):
    result = await db.execute(select(LostAndFound).filter(LostAndFound.userId == userId))
    return result.scalars().all()