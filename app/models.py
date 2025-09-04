from sqlalchemy import Column, Integer, String, Text, Date, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base

class Organization(Base):
    __tablename__ = 'organizations'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    subscription_tier = Column(String(50), nullable=False, default='free')

    users = relationship('User', back_populates='organization', cascade='all, delete')
    projects = relationship('Project', back_populates='organization', cascade='all, delete')

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False)
    organization_id = Column(Integer, ForeignKey('organizations.id', ondelete='CASCADE'), nullable=False)

    organization = relationship('Organization', back_populates='users')
    tasks = relationship('Task', back_populates='assigned_user')

class Project(Base):
    __tablename__ = 'projects'
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    due_date = Column(Date, nullable=True)
    org_id = Column(Integer, ForeignKey('organizations.id', ondelete='CASCADE'), nullable=False)

    organization = relationship('Organization', back_populates='projects')
    tasks = relationship('Task', back_populates='project', cascade='all, delete')

class Task(Base):
    __tablename__ = 'tasks'
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String(20), nullable=False, default='pending')
    due_date = Column(Date, nullable=True)
    project_id = Column(Integer, ForeignKey('projects.id', ondelete='CASCADE'), nullable=False)
    assigned_user_id = Column(Integer, ForeignKey('users.id', ondelete='SET NULL'), nullable=True)

    project = relationship('Project', back_populates='tasks')
    assigned_user = relationship('User', back_populates='tasks')
