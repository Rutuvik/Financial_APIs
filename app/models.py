from sqlalchemy import Column, Integer, String, DateTime
from .database import Base
from datetime import datetime
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String)
    password = Column(String)
    role = Column(String)
class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True)
    title = Column(String)
    company_name = Column(String)
    document_type = Column(String)
    file_path = Column(String)
    uploaded_by = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True)
    name = Column(String)