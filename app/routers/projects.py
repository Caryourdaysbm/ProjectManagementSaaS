from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from .. import models, schemas
from ..database import get_db
from ..security import get_current_user
from ..deps import require_admin

router = APIRouter(prefix="/projects", tags=["projects"])

@router.get("/", response_model=List[schemas.ProjectOut])
def list_projects(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return db.query(models.Project).filter(models.Project.org_id == current_user.organization_id).all()

@router.post("/", response_model=schemas.ProjectOut, status_code=201)
def create_project(project: schemas.ProjectCreate, db: Session = Depends(get_db), admin: models.User = Depends(require_admin)):
    p = models.Project(**project.model_dump(), org_id=admin.organization_id)
    db.add(p)
    db.commit()
    db.refresh(p)
    return p

@router.patch("/{project_id}", response_model=schemas.ProjectOut)
def update_project(project_id: int, project: schemas.ProjectCreate, db: Session = Depends(get_db), admin: models.User = Depends(require_admin)):
    p = db.get(models.Project, project_id)
    if not p or p.org_id != admin.organization_id:
        raise HTTPException(status_code=404, detail="Project not found")
    for k, v in project.model_dump().items():
        setattr(p, k, v)
    db.commit()
    db.refresh(p)
    return p

@router.delete("/{project_id}", status_code=204)
def delete_project(project_id: int, db: Session = Depends(get_db), admin: models.User = Depends(require_admin)):
    p = db.get(models.Project, project_id)
    if not p or p.org_id != admin.organization_id:
        raise HTTPException(status_code=404, detail="Project not found")
    db.delete(p)
    db.commit()
    return
