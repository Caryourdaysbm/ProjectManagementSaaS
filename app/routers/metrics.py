from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, case
from typing import List
from .. import models, schemas
from ..database import get_db
from ..security import get_current_user

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

@router.get("/metrics", response_model=schemas.MetricsOut)
def org_metrics(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    org_id = current_user.organization_id
    total_projects = db.query(models.Project).filter(models.Project.org_id == org_id).count()
    total_tasks = db.query(models.Task).join(models.Project).filter(models.Project.org_id == org_id).count()
    completed_tasks = db.query(models.Task).join(models.Project).filter(
        models.Project.org_id == org_id, models.Task.status == "done"
    ).count()
    return {"total_projects": total_projects, "total_tasks": total_tasks, "completed_tasks": completed_tasks}

@router.get("/projects_aggregate", response_model=List[schemas.ProjectAggOut])
def per_project_aggregate(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    org_id = current_user.organization_id
    q = (
        db.query(
            models.Project.id.label("project_id"),
            models.Project.title.label("title"),
            func.count(models.Task.id).label("total_tasks"),
            func.sum(case((models.Task.status == "done", 1), else_=0)).label("completed_tasks")
        )
        .outerjoin(models.Task, models.Task.project_id == models.Project.id)
        .filter(models.Project.org_id == org_id)
        .group_by(models.Project.id)
        .order_by(models.Project.id)
    )
    return [schemas.ProjectAggOut(**row._mapping) for row in q.all()]
