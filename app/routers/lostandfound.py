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
async def create_lostandfound(
    userId: int = Form(...),
    item_name: str = Form(...),
    isLost: bool = Form(...),
    desc: str = Form(...),
    date: str = Form(...),
    location: str = Form(...),
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
    result = await db.execute(select(LostAndFound))
    return result.scalars().all()

@router.get("/{item_id}", response_model=lostandfound_schema.LostAndFound)
async def get_lostandfound(item_id: str, db: AsyncSession = Depends(sessions.get_async_session)):
    result = await db.execute(select(LostAndFound).filter(LostAndFound.item_id == item_id))
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

@router.get("/{item_id}", response_model=lostandfound_schema.LostAndFound)
async def get_lostandfound(item_id: str, updated_item: lostandfound_schema.LostAndFound, db: AsyncSession = Depends(sessions.get_async_session)):
    result = await db.execute(select(LostAndFound).filter(LostAndFound.item_id == item_id))
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    for key, value in updated_item.dict(exclude_unset=True).items():
        if key != "item_id":
            item[key] = value
    await db.commit()
    await db.refresh(item)

@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_lostandfound(item_id: str, db: AsyncSession = Depends(sessions.get_async_session)):
    result = await db.execute(select(LostAndFound).filter(LostAndFound.item_id == item_id))
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    await db.delete(item)
    await db.commit()
    return None
