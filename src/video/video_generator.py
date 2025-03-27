from abc import ABC, abstractmethod
from loguru import logger

class VideoGenerator(ABC):
    """视频生成器抽象基类"""
    
    def __init__(self, config):
        """
        初始化视频生成器
        
        Args:
            config: 视频生成模型配置字典
        """
        self.config = config
        self.name = config.get('name', 'Unknown Video Generator')
        self.endpoint = config.get('endpoint')
        self.model = config.get('model')
        self.max_duration = config.get('max_duration', 4)  # 默认4秒
        
        # API密钥可能有不同的名称，由子类处理验证
    
    @abstractmethod
    def generate_video(self, description, output_path):
        """
        根据描述生成视频
        
        Args:
            description: 视频描述文本
            output_path: 输出视频文件路径
            
        Returns:
            输出视频文件路径
        """
        pass

from .kling_generator import KlingGenerator

def get_video_generator(config):
    """
    根据配置创建视频生成器
    
    Args:
        config: 视频生成模型配置字典
        
    Returns:
        VideoGenerator实例
    """
    name = config.get('name', '').lower()
    
    if '可灵' in name or 'kling' in name:
        return KlingGenerator(config)
    else:
        logger.error(f"不支持的视频生成模型类型: {name}")
        raise ValueError(f"不支持的视频生成模型类型: {name}")
