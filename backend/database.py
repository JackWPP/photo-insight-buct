from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 数据库文件路径
SQLALCHEMY_DATABASE_URL = "sqlite:///./photo_insight.db"

# 创建数据库引擎
# connect_args={"check_same_thread": False} 是 SQLite 的特殊要求，允许在多线程中使用
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# 创建数据库会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建一个 Base 类，我们的 ORM 模型将继承这个类
Base = declarative_base()

# 数据库依赖项
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
