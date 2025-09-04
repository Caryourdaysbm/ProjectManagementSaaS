from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from .security import get_current_user
from .database import get_db
from . import models

def require_admin(current_user: models.User = Depends(get_current_user)):
    if current_user.role != "Admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin only")
    return current_user

def require_same_org(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    # This dependency is a placeholder to emphasize multi-tenancy
    return current_user

def require_member_or_admin(current_user: models.User = Depends(get_current_user)):
    if current_user.role not in ("Admin", "Member"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized role")
    return current_user
