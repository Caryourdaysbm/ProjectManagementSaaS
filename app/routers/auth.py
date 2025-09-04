from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from .. import models, schemas
from ..database import get_db
from ..security import create_access_token, verify_password, hash_password

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register_org", response_model=schemas.OrganizationOut, status_code=201)
def register_org(payload: schemas.OrganizationCreate, db: Session = Depends(get_db)):
    # create org
    org = models.Organization(name=payload.org_name, subscription_tier=payload.subscription_tier)
    db.add(org)
    db.flush()
    # create admin user
    existing = db.query(models.User).filter(models.User.email == payload.admin_email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    admin = models.User(
        name=payload.admin_name,
        email=payload.admin_email,
        password_hash=hash_password(payload.password),
        role="Admin",
        organization_id=org.id
    )
    db.add(admin)
    db.commit()
    db.refresh(org)
    return org

@router.post("/login", response_model=schemas.Token)
def login(email: str, password: str, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    token = create_access_token({"sub": str(user.id), "org_id": user.organization_id, "role": user.role})
    return {"access_token": token, "token_type": "bearer"}
