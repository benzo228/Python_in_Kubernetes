from datetime import datetime
from typing import List, Optional
from .models import Task, TaskCreate

# Временное хранилище
tasks_db = {}
task_id_counter = 1

def get_all_tasks() -> List[Task]:
    return list(tasks_db.values())

def get_task(task_id: int) -> Optional[Task]:
    return tasks_db.get(task_id)

def create_task(task_data: TaskCreate) -> Task:
    global task_id_counter
    task = Task(
        id=task_id_counter,
        title=task_data.title,
        description=task_data.description,
        completed=task_data.completed,
        created_at=datetime.now()
    )
    tasks_db[task_id_counter] = task
    task_id_counter += 1
    return task

def update_task(task_id: int, task_data: TaskCreate) -> Optional[Task]:
    task = tasks_db.get(task_id)
    if not task:
        return None
    updated_task = Task(
        id=task_id,
        title=task_data.title,
        description=task_data.description,
        completed=task_data.completed,
        created_at=task.created_at
    )
    tasks_db[task_id] = updated_task
    return updated_task

def delete_task(task_id: int) -> bool:
    if task_id in tasks_db:
        del tasks_db[task_id]
        return True
    return False