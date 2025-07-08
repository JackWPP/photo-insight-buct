
import asyncio
import os
import socketio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
from sqlalchemy.orm import Session

# 导入数据库和模型相关的模块
from backend import crud, models, database, clip_model, vector_db

# 在应用启动时创建数据库表
models.Base.metadata.create_all(bind=database.engine)

# 日志配置
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 预加载模型，确保应用启动时模型就绪
if clip_model.model is None:
    logging.error("CLIP模型未能加载，应用可能无法正常处理图片特征。")

# 创建 FastAPI 应用
app = FastAPI()

# 配置 CORS 中间件,允许所有来源
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 创建 Socket.IO 服务
sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins='*')
socket_app = socketio.ASGIApp(sio, other_asgi_app=app)

@sio.event
async def connect(sid, environ):
    """客户端连接时触发"""
    logging.info(f"客户端连接成功: {sid}")
    await sio.emit('message', {'data': '连接成功！'}, room=sid)

@sio.event
async def disconnect(sid):
    """客户端断开连接时触发"""
    logging.info(f"客户端断开连接: {sid}")

@sio.on('start_indexing')
async def start_indexing(sid, data):
    """开始索引指定目录的图片并存入数据库"""
    directory = data.get('directory')
    if not directory or not os.path.isdir(directory):
        logging.error(f"无效的目录: {directory}")
        await sio.emit('error', {'data': '无效的目录或目录不存在'}, room=sid)
        return

    logging.info(f"开始扫描目录: {directory}")
    await sio.emit('indexing_status', {'data': f'开始扫描目录: {directory}'}, room=sid)

    supported_extensions = ('.jpg', '.jpeg', '.png', '.webp')
    db = database.SessionLocal()
    try:
        image_files = []
        for root, _, files in os.walk(directory):
            for file in files:
                if file.lower().endswith(supported_extensions):
                    image_files.append(os.path.join(root, file))
        
        total_files = len(image_files)
        await sio.emit('indexing_status', {'data': f'发现 {total_files} 张图片，准备开始处理...'}, room=sid)
        await asyncio.sleep(1)

        for i, file_path in enumerate(image_files):
            # 检查图片是否已完整索引
            db_image = crud.get_image_by_path(db, path=file_path)
            if db_image and db_image.vector_id:
                logging.info(f"图片已完整索引，跳过: {file_path}")
                continue

            # 发送当前处理状态到前端
            await sio.emit('indexing_status', {'data': f'({i+1}/{total_files}) 正在处理: {os.path.basename(file_path)}'}, room=sid)
            
            # 创建记录并生成向量
            new_image = crud.create_image_record(db, path=file_path)
            if new_image:
                logging.info(f"成功索引新图片: {file_path}")
                await sio.emit('new_image_found', {'path': new_image.path, 'status': 'Indexed'}, room=sid)
            else:
                # 可能是文件已存在但未向量化，或者创建失败
                logging.warning(f"未能为图片创建新索引记录 (可能已存在或出错): {file_path}")

            await asyncio.sleep(0.05) # 防止消息过于频繁

        logging.info(f"目录 {directory} 扫描完成")
        await sio.emit('indexing_complete', {'data': '所有图片处理完成!'})
    except Exception as e:
        logging.error(f"扫描过程中发生错误: {e}")
        await sio.emit('error', {'data': f'扫描出错: {str(e)}'}, room=sid)
    finally:
        db.close()

@sio.on('load_all_images')
async def load_all_images(sid, data):
    """从数据库加载所有已索引的图片"""
    logging.info("收到加载所有图片的请求")
    db = database.SessionLocal()
    try:
        images = crud.get_all_images(db)
        # 过滤掉那些还没有 vector_id 的不完整记录
        images_data = [{'path': image.path} for image in images if image.vector_id]
        await sio.emit('all_images_loaded', {'images': images_data}, room=sid)
        logging.info(f"已发送 {len(images_data)} 条完整索引记录到客户端")
    except Exception as e:
        logging.error(f"加载图片时发生错误: {e}")
        await sio.emit('error', {'data': f'加载图片出错: {str(e)}'}, room=sid)
    finally:
        db.close()

