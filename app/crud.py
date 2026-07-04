from datetime import datetime
from typing import List, Optional
from .models import Task, TaskCreate, TaskStatus, Comment, CommentCreate

# Хранилище
tasks_db = {}
task_id_counter = 1
comments_db = {}
comment_id_counter = 1

# ==================== Задачи ====================

def get_all_tasks(status: Optional[TaskStatus] = None) -> List[Task]:
    tasks = list(tasks_db.values())
    if status:
        tasks = [t for t in tasks if t.status == status]
    return tasks

def get_task(task_id: int) -> Optional[Task]:
    return tasks_db.get(task_id)

def create_task(task_data: TaskCreate) -> Task:
    global task_id_counter
    task = Task(
        id=task_id_counter,
        title=task_data.title,
        description=task_data.description,
        status=task_data.status,
        created_at=datetime.now(),
        updated_at=None,
        completed_at=None,
        comments=[]
    )
    tasks_db[task_id_counter] = task
    task_id_counter += 1
    return task

def update_task(task_id: int, task_data: TaskCreate) -> Optional[Task]:
    task = tasks_db.get(task_id)
    if not task:
        return None
    task.title = task_data.title
    task.description = task_data.description
    task.status = task_data.status
    task.updated_at = datetime.now()
    if task.status == TaskStatus.completed and task.completed_at is None:
        task.completed_at = datetime.now()
    elif task.status != TaskStatus.completed:
        task.completed_at = None
    return task

def update_task_status(task_id: int, status: TaskStatus) -> Optional[Task]:
    task = tasks_db.get(task_id)
    if not task:
        return None
    task.status = status
    task.updated_at = datetime.now()
    if status == TaskStatus.completed and task.completed_at is None:
        task.completed_at = datetime.now()
    elif status != TaskStatus.completed:
        task.completed_at = None
    return task

def delete_task(task_id: int) -> bool:
    if task_id in tasks_db:
        # Удаляем все комментарии к задаче
        for cid in list(comments_db.keys()):
            if comments_db[cid].task_id == task_id:
                del comments_db[cid]
        del tasks_db[task_id]
        return True
    return False

# ==================== Комментарии ====================

def get_comments_for_task(task_id: int) -> List[Comment]:
    return [c for c in comments_db.values() if c.task_id == task_id]

def create_comment(task_id: int, comment_data: CommentCreate) -> Optional[Comment]:
    if task_id not in tasks_db:
        return None
    global comment_id_counter
    comment = Comment(
        id=comment_id_counter,
        task_id=task_id,
        content=comment_data.content,
        created_at=datetime.now()
    )
    comments_db[comment_id_counter] = comment
    comment_id_counter += 1
    # Добавляем комментарий в задачу (для удобства)
    task = tasks_db[task_id]
    task.comments.append(comment)
    return comment

def delete_comment(comment_id: int) -> bool:
    if comment_id in comments_db:
        task_id = comments_db[comment_id].task_id
        del comments_db[comment_id]
        # Удаляем из задачи
        task = tasks_db.get(task_id)
        if task:
            task.comments = [c for c in task.comments if c.id != comment_id]
        return True
    return False