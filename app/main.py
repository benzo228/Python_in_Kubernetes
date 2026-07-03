from fastapi import FastAPI, Request, HTTPException, BackgroundTasks, Query
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from .models import TaskCreate, Task, TaskStatus, CommentCreate, Comment, StatusUpdate
from .crud import (
    get_all_tasks, get_task, create_task, update_task, delete_task,
    update_task_status, get_comments_for_task, create_comment, delete_comment
)
from .k8s_client import get_pods
import os
import logging
from typing import Optional, List

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Task Manager with K8s", version="2.0.0")

templates = Jinja2Templates(directory="app/templates")

# ==================== Health Checks ====================

@app.get("/live")
async def liveness():
    """Проверка, что приложение живо"""
    return {"status": "alive"}

@app.get("/ready")
async def readiness():
    """Проверка готовности (пока всегда OK)"""
    return {"status": "ready"}

# ==================== API Задачи ====================

@app.get("/api/tasks", response_model=List[Task])
async def list_tasks(
    status: Optional[TaskStatus] = Query(None, description="Фильтр по статусу")
):
    """Получить все задачи с возможной фильтрацией по статусу"""
    return get_all_tasks(status)

@app.post("/api/tasks", response_model=Task, status_code=201)
async def create_new_task(task: TaskCreate):
    """Создать новую задачу"""
    return create_task(task)

@app.get("/api/tasks/{task_id}", response_model=Task)
async def get_task_by_id(task_id: int):
    """Получить задачу по ID"""
    task = get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@app.put("/api/tasks/{task_id}", response_model=Task)
async def update_existing_task(task_id: int, task: TaskCreate):
    """Полностью обновить задачу"""
    updated = update_task(task_id, task)
    if not updated:
        raise HTTPException(status_code=404, detail="Task not found")
    return updated

@app.patch("/api/tasks/{task_id}/status", response_model=Task)
async def change_task_status(task_id: int, update: StatusUpdate):
    """Изменить статус задачи (тело: {"status": "completed"})"""
    updated = update_task_status(task_id, update.status)
    if not updated:
        raise HTTPException(status_code=404, detail="Task not found")
    return updated

@app.delete("/api/tasks/{task_id}", status_code=204)
async def delete_existing_task(task_id: int):
    """Удалить задачу (вместе с комментариями)"""
    deleted = delete_task(task_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"ok": True}

# ==================== API Комментарии ====================

@app.get("/api/tasks/{task_id}/comments", response_model=List[Comment])
async def get_comments(task_id: int):
    """Получить все комментарии к задаче"""
    if not get_task(task_id):
        raise HTTPException(status_code=404, detail="Task not found")
    return get_comments_for_task(task_id)

@app.post("/api/tasks/{task_id}/comments", response_model=Comment, status_code=201)
async def add_comment(task_id: int, comment: CommentCreate):
    """Добавить комментарий к задаче"""
    new_comment = create_comment(task_id, comment)
    if not new_comment:
        raise HTTPException(status_code=404, detail="Task not found")
    return new_comment

@app.delete("/api/comments/{comment_id}", status_code=204)
async def delete_comment_by_id(comment_id: int):
    """Удалить комментарий"""
    deleted = delete_comment(comment_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Comment not found")
    return {"ok": True}

# ==================== K8s API ====================

@app.get("/api/k8s/pods")
async def k8s_pods(namespace: str = "default"):
    """Получить список подов в указанном неймспейсе"""
    result = get_pods(namespace)
    if isinstance(result, dict) and "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])
    return {"pods": result}

# ==================== Фронтенд ====================

@app.get("/", response_class=HTMLResponse)
async def frontend(request: Request):
    """Главная страница с интерфейсом"""
    return templates.TemplateResponse("index.html", {"request": request})

# ==================== Для локального запуска ====================

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=True)