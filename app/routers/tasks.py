from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date, timedelta, datetime
from .. import models, schemas
from ..database import get_db
from ..security import get_current_user
from ..deps import require_member_or_admin

router = APIRouter(prefix="/tasks", tags=["tasks"])

def apply_org_scope(query, current_user: models.User):
    return query.join(models.Project).filter(models.Project.org_id == current_user.organization_id)

@router.get("/", response_model=List[schemas.TaskOut])
def list_tasks(
    status: Optional[str] = Query(default=None, pattern="^(pending|in_progress|done)$"),
    due: Optional[str] = Query(default=None, pattern="^(today|week)$"),
    project_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    q = db.query(models.Task)
    q = apply_org_scope(q, current_user)
    if status:
        q = q.filter(models.Task.status == status)
    if due == "today":
        today = date.today()
        q = q.filter(models.Task.due_date == today)
    elif due == "week":
        today = date.today()
        end = today + timedelta(days=7)
        q = q.filter(models.Task.due_date >= today, models.Task.due_date <= end)
    if project_id:
        q = q.filter(models.Task.project_id == project_id)
    return q.all()

@router.post("/", response_model=schemas.TaskOut, status_code=201)
def create_task(task: schemas.TaskCreate, db: Session = Depends(get_db), user: models.User = Depends(require_member_or_admin)):
    # check project belongs to org
    project = db.get(models.Project, task.project_id)
    if not project or project.org_id != user.organization_id:
        raise HTTPException(status_code=404, detail="Project not found")
    # Members can only create tasks for themselves
    if user.role == "Member":
        assigned_id = task.assigned_user_id or user.id
        if assigned_id != user.id:
            raise HTTPException(status_code=403, detail="Members can only create tasks for themselves")
    new_task = models.Task(
        title=task.title,
        description=task.description,
        status=task.status,
        due_date=task.due_date,
        project_id=task.project_id,
        assigned_user_id=task.assigned_user_id if user.role == "Admin" else user.id
    )
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task

@router.patch("/{task_id}", response_model=schemas.TaskOut)
def update_task(task_id: int, payload: schemas.TaskUpdate, db: Session = Depends(get_db), user: models.User = Depends(require_member_or_admin)):
    t = db.get(models.Task, task_id)
    if not t:
        raise HTTPException(status_code=404, detail="Task not found")
    # org scope
    if t.project.organization.id != user.organization_id:
        raise HTTPException(status_code=404, detail="Task not found")
    # members can update only their tasks
    if user.role == "Member" and t.assigned_user_id != user.id:
        raise HTTPException(status_code=403, detail="Members can only update their own tasks")
    data = payload.model_dump(exclude_unset=True)
    # members cannot reassign tasks to others
    if user.role == "Member" and "assigned_user_id" in data and data["assigned_user_id"] != user.id:
        raise HTTPException(status_code=403, detail="Members cannot reassign tasks")
    for k, v in data.items():
        setattr(t, k, v)
    db.commit()
    db.refresh(t)
    return t

@router.delete("/{task_id}", status_code=204)
def delete_task(task_id: int, db: Session = Depends(get_db), user: models.User = Depends(require_member_or_admin)):
    t = db.get(models.Task, task_id)
    if not t:
        raise HTTPException(status_code=404, detail="Task not found")
    if t.project.organization.id != user.organization_id:
        raise HTTPException(status_code=404, detail="Task not found")
    # Members can delete only their tasks
    if user.role == "Member" and t.assigned_user_id != user.id:
        raise HTTPException(status_code=403, detail="Members can only delete their own tasks")
    db.delete(t)
    db.commit()
    return
