from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
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

class SpringPhoto(Base):
    __tablename__ = "spring_photos"
    id = Column(Integer, primary_key=True, index=True)
    image_id = Column(Integer, ForeignKey("images.id"), unique=True)
    image = relationship("Image")

class SummerPhoto(Base):
    __tablename__ = "summer_photos"
    id = Column(Integer, primary_key=True, index=True)
    image_id = Column(Integer, ForeignKey("images.id"), unique=True)
    image = relationship("Image")

class AutumnPhoto(Base):
    __tablename__ = "autumn_photos"
    id = Column(Integer, primary_key=True, index=True)
    image_id = Column(Integer, ForeignKey("images.id"), unique=True)
    image = relationship("Image")

class WinterPhoto(Base):
    __tablename__ = "winter_photos"
    id = Column(Integer, primary_key=True, index=True)
    image_id = Column(Integer, ForeignKey("images.id"), unique=True)
    image = relationship("Image")
