from transformers import CLIPProcessor, CLIPModel
from PIL import Image
import torch
import logging

# 配置
MODEL_NAME = "openai/clip-vit-base-patch32"
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

logging.info(f"CLIP 模型正在使用设备: {DEVICE}")

# 全局加载模型和处理器，避免重复加载
try:
    model = CLIPModel.from_pretrained(MODEL_NAME).to(DEVICE)
    processor = CLIPProcessor.from_pretrained(MODEL_NAME)
    logging.info(f"CLIP 模型 '{MODEL_NAME}' 加载成功")
except Exception as e:
    logging.error(f"加载 CLIP 模型失败: {e}")
    model = None
    processor = None

def get_image_features(image_path: str):
    """
    为单个图片生成特征向量。
    :param image_path: 图片文件的绝对路径。
    :return: 图片的特征向量 (numpy array) 或在失败时返回 None。
    """
    if not model or not processor:
        logging.error("CLIP 模型未正确加载，无法提取特征。")
        return None

    try:
        image = Image.open(image_path).convert("RGB")
        inputs = processor(images=image, return_tensors="pt", padding=True, truncation=True).to(DEVICE)
        with torch.no_grad():
            image_features = model.get_image_features(**inputs)
        
        # 将向量移动到 CPU 并转换为 numpy 数组
        return image_features.cpu().numpy().flatten()
    except FileNotFoundError:
        logging.error(f"图片文件未找到: {image_path}")
        return None
    except Exception as e:
        logging.error(f"提取图片特征时发生错误 ({image_path}): {e}")
        return None
