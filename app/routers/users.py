from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from .. import models, schemas
from ..database import get_db
from ..deps import require_admin
from ..security import hash_password

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/invite", response_model=schemas.UserOut, status_code=201)
def invite_user(user: schemas.UserCreate, db: Session = Depends(get_db), admin: models.User = Depends(require_admin)):
    # ensure unique email and same org
    if db.query(models.User).filter(models.User.email == user.email).first():
        raise HTTPException(status_code=400, detail="Email already exists")
    new_user = models.User(
        name=user.name,
        email=user.email,
        password_hash=hash_password(user.password),
        role=user.role,
        organization_id=admin.organization_id
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.get("/", response_model=List[schemas.UserOut])
def list_users(db: Session = Depends(get_db), admin: models.User = Depends(require_admin)):
    return db.query(models.User).filter(models.User.organization_id == admin.organization_id).all()

@router.patch("/{user_id}/role", response_model=schemas.UserOut)
def update_role(user_id: int, role: str, db: Session = Depends(get_db), admin: models.User = Depends(require_admin)):
    user = db.get(models.User, user_id)
    if not user or user.organization_id != admin.organization_id:
        raise HTTPException(status_code=404, detail="User not found")
    if role not in ("Admin", "Member"):
        raise HTTPException(status_code=400, detail="Invalid role")
    user.role = role
    db.commit()
    db.refresh(user)
    return user
