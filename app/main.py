import logging
import os
from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Query, Request
from fastapi.responses import HTMLResponse
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from . import crud, models, schemas
from .auth import (
    create_access_token,
    get_current_user,
    get_password_hash,
    verify_password,
)
from .database import Base, engine, get_db
from .k8s_client import get_pods

DbSession = Annotated[AsyncSession, Depends(get_db)]

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables created (if not exist)")
    yield
    await engine.dispose()

app = FastAPI(title="Task Manager with K8s", version="4.0.0", lifespan=lifespan)
templates = Jinja2Templates(directory="app/templates")

# ==================== Health Checks ====================
@app.get("/live")
async def liveness(): return {"status": "alive"}

@app.get("/ready")
async def readiness(db: DbSession):
    try:
        await db.execute("SELECT 1")
        return {"status": "ready"}
    except SQLAlchemyError:
        raise HTTPException(status_code=503, detail="Database unavailable")

# ==================== Auth ====================
@app.post("/api/auth/register", response_model=schemas.UserResponse)
async def register(user: schemas.UserCreate, db: DbSession):
    result = await db.execute(select(models.User).where(models.User.username == user.username))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Username already registered")
    
    db_user = models.User(username=user.username, hashed_password=get_password_hash(user.password))
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user

@app.post("/api/auth/login", response_model=schemas.Token)
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: DbSession):
    result = await db.execute(select(models.User).where(models.User.username == form_data.username))
    user = result.scalar_one_or_none()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

# ==================== API Tasks ====================
@app.get("/api/tasks", response_model=list[schemas.Task])
async def list_tasks(
    status: Annotated[schemas.TaskStatus | None, Query()] = None,
    db: DbSession = None,
    current_user: models.User = Depends(get_current_user)
):
    return await crud.get_all_tasks(db, current_user.id, status)

@app.post("/api/tasks", response_model=schemas.Task, status_code=201)
async def create_new_task(task: schemas.TaskCreate, db: DbSession, current_user: models.User = Depends(get_current_user)):
    return await crud.create_task(db, task, current_user.id)

@app.get("/api/tasks/{task_id}", response_model=schemas.Task)
async def get_task_by_id(task_id: int, db: DbSession, current_user: models.User = Depends(get_current_user)):
    task = await crud.get_task(db, task_id, current_user.id)
    if not task: raise HTTPException(status_code=404, detail="Task not found")
    return task

@app.put("/api/tasks/{task_id}", response_model=schemas.Task)
async def update_existing_task(task_id: int, task: schemas.TaskCreate, db: DbSession, current_user: models.User = Depends(get_current_user)):
    updated = await crud.update_task(db, task_id, task, current_user.id)
    if not updated: raise HTTPException(status_code=404, detail="Task not found")
    return updated

@app.patch("/api/tasks/{task_id}/status", response_model=schemas.Task)
async def change_task_status(task_id: int, update: schemas.StatusUpdate, db: DbSession, current_user: models.User = Depends(get_current_user)):
    updated = await crud.update_task_status(db, task_id, update.status, current_user.id)
    if not updated: raise HTTPException(status_code=404, detail="Task not found")
    return updated

@app.delete("/api/tasks/{task_id}", status_code=204)
async def delete_existing_task(task_id: int, db: DbSession, current_user: models.User = Depends(get_current_user)):
    deleted = await crud.delete_task(db, task_id, current_user.id)
    if not deleted: raise HTTPException(status_code=404, detail="Task not found")
    return {"ok": True}

# ==================== API Comments ====================
@app.get("/api/tasks/{task_id}/comments", response_model=list[schemas.Comment])
async def get_comments(task_id: int, db: DbSession, current_user: models.User = Depends(get_current_user)):
    if not await crud.get_task(db, task_id, current_user.id):
        raise HTTPException(status_code=404, detail="Task not found")
    return await crud.get_comments_for_task(db, task_id)

@app.post("/api/tasks/{task_id}/comments", response_model=schemas.Comment, status_code=201)
async def add_comment(task_id: int, comment: schemas.CommentCreate, db: DbSession, current_user: models.User = Depends(get_current_user)):
    new_comment = await crud.create_comment(db, task_id, comment)
    if not new_comment: raise HTTPException(status_code=404, detail="Task not found")
    return new_comment

@app.delete("/api/comments/{comment_id}", status_code=204)
async def delete_comment_by_id(comment_id: int, db: DbSession, current_user: models.User = Depends(get_current_user)):
    deleted = await crud.delete_comment(db, comment_id)
    if not deleted: raise HTTPException(status_code=404, detail="Comment not found")
    return {"ok": True}

# ==================== K8s API ====================
@app.get("/api/k8s/pods")
async def k8s_pods(namespace: str = "default", current_user: models.User = Depends(get_current_user)):
    result = get_pods(namespace)
    if isinstance(result, dict) and "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])
    return {"pods": result}

# ==================== Frontend ====================
@app.get("/", response_class=HTMLResponse)
async def frontend(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=False)