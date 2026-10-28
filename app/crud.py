from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from datetime import datetime
from typing import Optional, List
from . import models, schemas

# ==================== Tasks ====================

async def get_all_tasks(db: AsyncSession, status: Optional[str] = None) -> List[models.Task]:
    query = select(models.Task).options(selectinload(models.Task.comments))
    if status:
        query = query.where(models.Task.status == status)
    result = await db.execute(query)
    return result.scalars().all()

async def get_task(db: AsyncSession, task_id: int) -> Optional[models.Task]:
    result = await db.execute(select(models.Task).where(models.Task.id == task_id))
    return result.scalar_one_or_none()

async def create_task(db: AsyncSession, task_data: schemas.TaskCreate) -> models.Task:
    db_task = models.Task(**task_data.model_dump())
    db.add(db_task)
    await db.commit()
    await db.refresh(db_task)
    return db_task

async def update_task(db: AsyncSession, task_id: int, task_data: schemas.TaskCreate) -> Optional[models.Task]:
    task = await get_task(db, task_id)
    if not task:
        return None
    task.title = task_data.title
    task.description = task_data.description
    task.status = task_data.status
    task.updated_at = datetime.utcnow()
    if task.status == schemas.TaskStatus.completed and task.completed_at is None:
        task.completed_at = datetime.utcnow()
    await db.commit()
    await db.refresh(task)
    return task

async def update_task_status(db: AsyncSession, task_id: int, status: schemas.TaskStatus) -> Optional[models.Task]:
    task = await get_task(db, task_id)
    if not task:
        return None
    task.status = status
    task.updated_at = datetime.utcnow()
    if status == schemas.TaskStatus.completed and task.completed_at is None:
        task.completed_at = datetime.utcnow()
    await db.commit()
    await db.refresh(task)
    return task

async def delete_task(db: AsyncSession, task_id: int) -> bool:
    task = await get_task(db, task_id)
    if not task:
        return False
    await db.delete(task)
    await db.commit()
    return True

# ==================== Comments ====================

async def get_comments_for_task(db: AsyncSession, task_id: int) -> List[models.Comment]:
    result = await db.execute(select(models.Comment).where(models.Comment.task_id == task_id))
    return result.scalars().all()

async def create_comment(db: AsyncSession, task_id: int, comment_data: schemas.CommentCreate) -> Optional[models.Comment]:
    task = await get_task(db, task_id)
    if not task:
        return None
    db_comment = models.Comment(task_id=task_id, content=comment_data.content)
    db.add(db_comment)
    await db.commit()
    await db.refresh(db_comment)
    return db_comment

async def delete_comment(db: AsyncSession, comment_id: int) -> bool:
    result = await db.execute(delete(models.Comment).where(models.Comment.id == comment_id))
    if result.rowcount == 0:
        return False
    await db.commit()
    return True