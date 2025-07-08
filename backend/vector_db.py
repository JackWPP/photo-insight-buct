import chromadb
import logging

# 配置
DB_PATH = "./chroma_db"
COLLECTION_NAME = "image_vectors"

# 初始化 ChromaDB 客户端
# 使用持久化存储，确保数据在重启后依然存在
client = chromadb.PersistentClient(path=DB_PATH)

# 获取或创建集合
try:
    collection = client.get_or_create_collection(name=COLLECTION_NAME)
    logging.info(f"ChromaDB 集合 '{COLLECTION_NAME}' 加载/创建成功")
except Exception as e:
    logging.error(f"加载/创建 ChromaDB 集合失败: {e}")
    collection = None

def add_vector(vector, vector_id: str):
    """
    向 ChromaDB 集合中添加一个向量。
    :param vector: 图片的特征向量。
    :param vector_id: 与 SQLite 中图片记录关联的唯一 ID。
    :return: 如果成功则返回 True，否则返回 False。
    """
    if collection is None:
        logging.error("ChromaDB 集合未初始化，无法添加向量。")
        return False
    try:
        collection.add(
            embeddings=[vector.tolist()], # 确保 embedding 是 list
            ids=[vector_id]
        )
        logging.info(f"成功将向量 (ID: {vector_id}) 添加到 ChromaDB")
        return True
    except Exception as e:
        logging.error(f"向 ChromaDB 添加向量时出错 (ID: {vector_id}): {e}")
        return False

def get_vector_count():
    """获取集合中的向量总数"""
    if collection is None:
        return 0
    return collection.count()
