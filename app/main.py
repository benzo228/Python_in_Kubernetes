from fastapi import FastAPI, Request, HTTPException, BackgroundTasks
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from .models import TaskCreate, Task
from .crud import get_all_tasks, get_task, create_task, update_task, delete_task
from .k8s_client import get_pods
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Task Manager with K8s", version="1.0.0")

# Шаблоны для фронтенда
templates = Jinja2Templates(directory="app/templates")

# ==================== API Эндпоинты ====================

@app.get("/api/tasks", response_model=list[Task])
async def list_tasks():
    """Получить все задачи"""
    return get_all_tasks()

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
    """Обновить задачу"""
    updated = update_task(task_id, task)
    if not updated:
        raise HTTPException(status_code=404, detail="Task not found")
    return updated

@app.delete("/api/tasks/{task_id}", status_code=204)
async def delete_existing_task(task_id: int):
    """Удалить задачу"""
    deleted = delete_task(task_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"ok": True}

@app.get("/api/k8s/pods")
async def k8s_pods(namespace: str = "default"):
    """Получить список подов в указанном неймспейсе"""
    result = get_pods(namespace)
    if isinstance(result, dict) and "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])
    return {"pods": result}

# ==================== Фронтенд (HTML) ====================

@app.get("/", response_class=HTMLResponse)
async def frontend(request: Request):
    """Главная страница с интерфейсом"""
    return templates.TemplateResponse("index.html", {"request": request})

# ==================== Healthcheck ====================

@app.get("/health")
async def health():
    return {"status": "ok"}

# ==================== Для локального запуска ====================

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=True)