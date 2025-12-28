from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.dialects.postgresql import JSON, ARRAY
from database import Base
from datetime import datetime
from sqlalchemy.dialects.postgresql import TSVECTOR
import uuid

class Note(Base):
    __tablename__ = 'notes'

    id = Column(Integer, primary_key=True, index=True)
    content = Column(String, index=True)
    tags = Column(ARRAY(String))
    createdAt = Column(DateTime, default=datetime.now)
    lastupdated = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    user_id = Column(String(36), ForeignKey("user.user_id"), nullable=False)

    search_vector = Column(TSVECTOR)


class User(Base):
    __tablename__ = 'user'

    user_id = Column(String(36), primary_key=True, default = lambda: str(uuid.uuid4()))
    username = Column(String)
    password = Column(String)
    created = Column(DateTime, default=datetime.now)