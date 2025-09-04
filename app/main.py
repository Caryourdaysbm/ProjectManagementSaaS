from fastapi import FastAPI
from .database import Base, engine
from .routers import auth, users, organizations, projects, tasks, metrics

# Ensure metadata is available for Alembic; do not create_all here (migrations handle schema)

app = FastAPI(title="PM SaaS API", version="0.1.0")

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(organizations.router)
app.include_router(projects.router)
app.include_router(tasks.router)
app.include_router(metrics.router)
