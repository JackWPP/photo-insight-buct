from sqlalchemy.orm import Session
from . import models, clip_model, vector_db
import os
import datetime
import uuid
import logging

def get_image_by_path(db: Session, path: str):
    """根据路径查询图片"""
    return db.query(models.Image).filter(models.Image.path == path).first()

def create_image_record(db: Session, path: str):
    """创建新的图片记录, 包括生成和存储特征向量。"""
    # 检查记录是否已存在且已向量化
    db_image = get_image_by_path(db, path)
    if db_image and db_image.vector_id:
        logging.info(f"图片已完整索引，跳过: {path}")
        return None

    # 如果记录不存在，先创建基础元数据记录
    if not db_image:
        try:
            file_stat = os.stat(path)
            db_image = models.Image(
                path=path,
                filename=os.path.basename(path),
                size_mb=round(file_stat.st_size / (1024 * 1024), 2),
                created_at=datetime.datetime.fromtimestamp(file_stat.st_ctime),
                indexed_at=datetime.datetime.utcnow()
            )
            db.add(db_image)
            db.commit()
            db.refresh(db_image)
        except FileNotFoundError:
            logging.error(f"创建记录时文件未找到: {path}")
            db.rollback()
            return None
        except Exception as e:
            logging.error(f"创建初始数据库记录时出错 ({path}): {e}")
            db.rollback()
            return None

    # 为图片生成并存储特征向量
    try:
        logging.info(f"正在为图片生成特征向量: {path}")
        features = clip_model.get_image_features(path)
        if features is None:
            logging.error(f"为图片生成特征向量失败: {path}")
            return None

        vector_id = str(uuid.uuid4())
        if not vector_db.add_vector(features, vector_id):
            logging.error(f"无法将向量存入 ChromaDB: {path}")
            return None
        
        # 更新 SQLite 记录以包含 vector_id
        db_image.vector_id = vector_id
        db.commit()
        db.refresh(db_image)
        logging.info(f"成功为图片创建向量并更新记录: {path}")
        return db_image

    except Exception as e:
        logging.error(f"向量化或数据库更新过程中出错 ({path}): {e}")
        db.rollback()
        return None

def get_all_images(db: Session):
    """获取所有已索引的图片"""
    return db.query(models.Image).all()

def add_photo_to_season(db: Session, image_id: int, season_model):
    """将照片添加进指定的季节表"""
    # 检查是否已存在
    existing_entry = db.query(season_model).filter(season_model.image_id == image_id).first()
    if existing_entry:
        return existing_entry
    
    db_season_photo = season_model(image_id=image_id)
    db.add(db_season_photo)
    db.commit()
    db.refresh(db_season_photo)
    return db_season_photo

def add_photo_to_spring(db: Session, image_id: int):
    return add_photo_to_season(db, image_id, models.SpringPhoto)

def add_photo_to_summer(db: Session, image_id: int):
    return add_photo_to_season(db, image_id, models.SummerPhoto)

def add_photo_to_autumn(db: Session, image_id: int):
    return add_photo_to_season(db, image_id, models.AutumnPhoto)

def add_photo_to_winter(db: Session, image_id: int):
    return add_photo_to_season(db, image_id, models.WinterPhoto)

def get_spring_photos(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Image).join(models.SpringPhoto).offset(skip).limit(limit).all()

def get_summer_photos(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Image).join(models.SummerPhoto).offset(skip).limit(limit).all()

def get_autumn_photos(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Image).join(models.AutumnPhoto).offset(skip).limit(limit).all()

def get_winter_photos(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Image).join(models.WinterPhoto).offset(skip).limit(limit).all()
