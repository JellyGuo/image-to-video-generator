import os
import base64
from PIL import Image
from loguru import logger

def load_image(image_path):
    """
    加载图片文件
    
    Args:
        image_path: 图片文件路径
        
    Returns:
        PIL.Image对象
    """
    try:
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"图片文件不存在: {image_path}")
        
        image = Image.open(image_path)
        logger.info(f"成功加载图片: {image_path}, 尺寸: {image.size}")
        return image
    except Exception as e:
        logger.error(f"加载图片失败: {e}")
        raise

def encode_image_base64(image_path):
    """
    将图片编码为base64字符串
    
    Args:
        image_path: 图片文件路径
        
    Returns:
        base64编码的字符串
    """
    try:
        with open(image_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
        logger.info(f"成功将图片编码为base64: {image_path}")
        return encoded_string
    except Exception as e:
        logger.error(f"图片base64编码失败: {e}")
        raise

def resize_image(image, max_size=1024):
    """
    调整图片大小，保持宽高比
    
    Args:
        image: PIL.Image对象
        max_size: 最大尺寸（宽或高）
        
    Returns:
        调整大小后的PIL.Image对象
    """
    width, height = image.size
    
    # 如果图片尺寸已经小于最大尺寸，则不调整
    if width <= max_size and height <= max_size:
        return image
    
    # 计算调整后的尺寸
    if width > height:
        new_width = max_size
        new_height = int(height * max_size / width)
    else:
        new_height = max_size
        new_width = int(width * max_size / height)
    
    # 调整图片大小
    resized_image = image.resize((new_width, new_height), Image.LANCZOS)
    logger.info(f"图片尺寸已调整: {image.size} -> {resized_image.size}")
    
    return resized_image

def save_image(image, output_path):
    """
    保存图片
    
    Args:
        image: PIL.Image对象
        output_path: 输出文件路径
    """
    try:
        # 确保输出目录存在
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        image.save(output_path)
        logger.info(f"图片已保存: {output_path}")
    except Exception as e:
        logger.error(f"保存图片失败: {e}")
        raise
