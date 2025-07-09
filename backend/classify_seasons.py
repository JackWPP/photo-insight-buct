import base64
import logging
import os
import asyncio
import requests
import json
from PIL import Image
import io

from . import crud, models, database

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def image_to_base64(image_path: str, max_size=1024):
    """
    将图片文件转换为 Base64 编码, 并在转换前将其等比缩小。
    """
    try:
        with Image.open(image_path) as img:
            # 维持宽高比进行缩小
            img.thumbnail((max_size, max_size))
            
            # 将图像保存到内存中的字节缓冲区
            buffered = io.BytesIO()
            # 确保保存为 JPEG 格式以兼容大多数 VLM
            if img.mode == 'RGBA':
                img = img.convert('RGB')
            img.save(buffered, format="JPEG")
            
            # 从缓冲区获取字节并进行 Base64 编码
            return base64.b64encode(buffered.getvalue()).decode('utf-8')
            
    except FileNotFoundError:
        logging.error(f"图片文件未找到: {image_path}")
        return None
    except Exception as e:
        logging.error(f"转换和缩放图片 '{os.path.basename(image_path)}' 时出错: {e}")
        return None


import requests
import json

# ... (其他导入)

def classify_image_season(image_path: str):
    """使用本地 VLM 模型判断图片所属的季节。"""
    base64_image = image_to_base64(image_path)
    if not base64_image:
        return None

    headers = {
        "Content-Type": "application/json",
        # 模拟 curl 的 User-Agent，排除任何可能由 python-requests 引入的变量
        "User-Agent": "curl/7.81.0" 
    }
    payload = {
        "model": "gemma/gemma2-9b-it", # 请确保这里的模型名称与您在 LM Studio 中加载的一致
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Analyze the following image and determine which of the four seasons it best represents: Spring, Summer, Autumn, or Winter. Respond with only one word from the list: [Spring, Summer, Autumn, Winter]."},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                ]
            }
        ],
        "max_tokens": 10,
    }
    
    api_url = "http://localhost:1234/v1/chat/completions"

    try:
        # 手动将 payload 编码为 UTF-8 字符串，并使用 data 参数发送
        # 这与 curl -d '...' 的行为完全一致
        response = requests.post(api_url, headers=headers, data=json.dumps(payload).encode('utf-8'), timeout=60)
        
        # 检查 HTTP 状态码
        if response.status_code == 200:
            season = response.json()['choices'][0]['message']['content'].strip().capitalize()
            return season
        elif response.status_code == 502:
            logging.error(f"接收到来自 VLM 服务的 502 Bad Gateway 错误。这通常意味着模型本身在处理图片 '{os.path.basename(image_path)}' 时崩溃或失败。请检查 LM Studio 的日志。")
            return None
        else:
            logging.error(f"调用 VLM API 时收到非预期的状态码 {response.status_code}: {response.text}")
            return None

    except requests.exceptions.RequestException as e:
        logging.error(f"使用 requests 调用 VLM API 时发生网络错误: {e}")
        return None
    except Exception as e:
        logging.error(f"处理 API 响应时发生未知错误: {e}")
        return None

async def classification_task(sio=None, sid=None):
    """
    ���行分类的核心任务。
    如果提供了 sio 和 sid，则通过 Socket.IO 发送进度更新。
    """
    logging.info("开始季节分类任务...")
    if sio and sid:
        await sio.emit('classification_status', {'data': '分类任务已开始...'}, room=sid)

    db = database.SessionLocal()
    try:
        images = crud.get_all_images(db)
        images_to_classify = [img for img in images if img.vector_id]
        total_images = len(images_to_classify)
        
        logging.info(f"发现 {total_images} 张需要分类的图片。")
        if sio and sid:
            await sio.emit('classification_status', {'data': f'发现 {total_images} 张需要分类的图片。'}, room=sid)
            await asyncio.sleep(1)

        season_map = {
            "Spring": crud.add_photo_to_spring,
            "Summer": crud.add_photo_to_summer,
            "Autumn": crud.add_photo_to_autumn,
            "Winter": crud.add_photo_to_winter,
        }

        for i, image in enumerate(images_to_classify):
            status_msg = f"({i+1}/{total_images}) 正在分类: {os.path.basename(image.path)}"
            logging.info(status_msg)
            if sio and sid:
                await sio.emit('classification_status', {'data': status_msg}, room=sid)

            # 在循环内部调用，以避免阻塞事件循环太久
            loop = asyncio.get_event_loop()
            season = await loop.run_in_executor(None, classify_image_season, image.path)
            
            if season and season in season_map:
                try:
                    season_map[season](db, image_id=image.id)
                    logging.info(f"成功将图片 ID {image.id} 添加到 {season} 表中。")
                except Exception as e:
                    if "UNIQUE constraint failed" in str(e):
                        logging.warning(f"图片 ID {image.id} 已在 {season} 表中，跳过。")
                    else:
                        logging.error(f"添加图片 ID {image.id} 到数据库时出错: {e}")
            elif season:
                logging.warning(f"模型返回未知分类: '{season}'，跳过图片。")
            else:
                logging.warning(f"未能确定图片 '{image.path}' 的季节，跳过。")
            
            await asyncio.sleep(0.05)

        logging.info("所有图片季节分类任务完成。")
        if sio and sid:
            await sio.emit('classification_complete', {'data': '所有图片季节分类完成！'}, room=sid)

    except Exception as e:
        logging.error(f"分类过程中发生严重错误: {e}")
        if sio and sid:
            await sio.emit('error', {'data': f'分类出错: {str(e)}'}, room=sid)
    finally:
        db.close()

if __name__ == "__main__":
    models.Base.metadata.create_all(bind=database.engine)
    asyncio.run(classification_task())
