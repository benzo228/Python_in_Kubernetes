from fastapi import FastAPI, Request, HTTPException, Depends, Query
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from contextlib import asynccontextmanager
from .database import get_db, engine, Base
from . import schemas, crud
from .k8s_client import get_pods
import os
import logging
from typing import Optional, List

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: создаём таблицы
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables created (if not exist)")
    yield
    # Shutdown
    await engine.dispose()

app = FastAPI(title="Task Manager with K8s", version="3.0.0", lifespan=lifespan)

templates = Jinja2Templates(directory="app/templates")

# ==================== Health Checks ====================

@app.get("/live")
async def liveness():
    return {"status": "alive"}

@app.get("/ready")
async def readiness(db: AsyncSession = Depends(get_db)):
    # Проверяем подключение к БД
    try:
        await db.execute("SELECT 1")
        return {"status": "ready"}
    except Exception:
        raise HTTPException(status_code=503, detail="Database unavailable")

# ==================== API Tasks ====================

@app.get("/api/tasks", response_model=List[schemas.Task])
async def list_tasks(
    status: Optional[schemas.TaskStatus] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    return await crud.get_all_tasks(db, status)

@app.post("/api/tasks", response_model=schemas.Task, status_code=201)
async def create_new_task(task: schemas.TaskCreate, db: AsyncSession = Depends(get_db)):
    return await crud.create_task(db, task)

@app.get("/api/tasks/{task_id}", response_model=schemas.Task)
async def get_task_by_id(task_id: int, db: AsyncSession = Depends(get_db)):
    task = await crud.get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@app.put("/api/tasks/{task_id}", response_model=schemas.Task)
async def update_existing_task(task_id: int, task: schemas.TaskCreate, db: AsyncSession = Depends(get_db)):
    updated = await crud.update_task(db, task_id, task)
    if not updated:
        raise HTTPException(status_code=404, detail="Task not found")
    return updated

@app.patch("/api/tasks/{task_id}/status", response_model=schemas.Task)
async def change_task_status(task_id: int, update: schemas.StatusUpdate, db: AsyncSession = Depends(get_db)):
    updated = await crud.update_task_status(db, task_id, update.status)
    if not updated:
        raise HTTPException(status_code=404, detail="Task not found")
    return updated

@app.delete("/api/tasks/{task_id}", status_code=204)
async def delete_existing_task(task_id: int, db: AsyncSession = Depends(get_db)):
    deleted = await crud.delete_task(db, task_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"ok": True}

# ==================== API Comments ====================

@app.get("/api/tasks/{task_id}/comments", response_model=List[schemas.Comment])
async def get_comments(task_id: int, db: AsyncSession = Depends(get_db)):
    if not await crud.get_task(db, task_id):
        raise HTTPException(status_code=404, detail="Task not found")
    return await crud.get_comments_for_task(db, task_id)

@app.post("/api/tasks/{task_id}/comments", response_model=schemas.Comment, status_code=201)
async def add_comment(task_id: int, comment: schemas.CommentCreate, db: AsyncSession = Depends(get_db)):
    new_comment = await crud.create_comment(db, task_id, comment)
    if not new_comment:
        raise HTTPException(status_code=404, detail="Task not found")
    return new_comment

@app.delete("/api/comments/{comment_id}", status_code=204)
async def delete_comment_by_id(comment_id: int, db: AsyncSession = Depends(get_db)):
    deleted = await crud.delete_comment(db, comment_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Comment not found")
    return {"ok": True}

# ==================== K8s API ====================

@app.get("/api/k8s/pods")
async def k8s_pods(namespace: str = "default"):
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