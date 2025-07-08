from sqlalchemy import Column, Integer, String, Float, DateTime
from .database import Base
import datetime

class Image(Base):
    __tablename__ = "images"

    id = Column(Integer, primary_key=True, index=True)
    path = Column(String, unique=True, index=True, nullable=False)
    filename = Column(String, nullable=False)
    size_mb = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    indexed_at = Column(DateTime, default=datetime.datetime.utcnow)
    vector_id = Column(String, unique=True, index=True, nullable=True) # 存储在 ChromaDB 中的唯一 ID
