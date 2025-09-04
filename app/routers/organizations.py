from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import models, schemas
from ..database import get_db
from ..security import get_current_user

router = APIRouter(prefix="/organizations", tags=["organizations"])

@router.get("/me", response_model=schemas.OrganizationOut)
def get_my_org(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    org = db.get(models.Organization, current_user.organization_id)
    return org
