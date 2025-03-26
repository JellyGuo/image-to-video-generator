import requests
import json
import time
import os
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

class RunwayGenerator(VideoGenerator):
    """Runway Gen-2 API客户端"""
    
    def __init__(self, config):
        """初始化Runway生成器"""
        super().__init__(config)
        self.api_key = config.get('api_key')
        
        if not self.endpoint or not self.api_key:
            raise ValueError(f"Runway配置不完整: endpoint={self.endpoint}, api_key={'已设置' if self.api_key else '未设置'}")
    
    def generate_video(self, description, output_path):
        """
        使用Runway Gen-2 API根据描述生成视频
        
        Args:
            description: 视频描述文本
            output_path: 输出视频文件路径
            
        Returns:
            输出视频文件路径
        """
        logger.info(f"使用{self.name}生成视频")
        
        try:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            
            payload = {
                "prompt": description,
                "model": self.model,
                "mode": "text-to-video",
                "duration": self.max_duration
            }
            
            # 发送生成请求
            response = requests.post(f"{self.endpoint}", headers=headers, json=payload)
            response.raise_for_status()
            
            result = response.json()
            job_id = result.get('id')
            
            if not job_id:
                raise ValueError("未能获取视频生成任务ID")
            
            logger.info(f"视频生成任务已提交，任务ID: {job_id}")
            
            # 轮询检查任务状态
            status_url = f"{self.endpoint}/{job_id}"
            video_url = None
            
            while True:
                status_response = requests.get(status_url, headers=headers)
                status_response.raise_for_status()
                
                status_data = status_response.json()
                status = status_data.get('status')
                
                if status == 'completed':
                    video_url = status_data.get('output')
                    break
                elif status == 'failed':
                    error_message = status_data.get('error', '未知错误')
                    raise RuntimeError(f"视频生成失败: {error_message}")
                
                logger.info(f"视频生成中，当前状态: {status}")
                time.sleep(5)  # 等待5秒后再次检查
            
            if not video_url:
                raise ValueError("未能获取生成的视频URL")
            
            # 下载视频
            logger.info(f"开始下载生成的视频: {video_url}")
            
            # 确保输出目录存在
            output_dir = os.path.dirname(output_path)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir)
            
            video_response = requests.get(video_url, stream=True)
            video_response.raise_for_status()
            
            with open(output_path, 'wb') as f:
                for chunk in video_response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            logger.info(f"视频已保存: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"生成视频失败: {e}")
            raise

class PikaGenerator(VideoGenerator):
    """Pika Labs API客户端"""
    
    def __init__(self, config):
        """初始化Pika生成器"""
        super().__init__(config)
        self.api_key = config.get('api_key')
        
        if not self.endpoint or not self.api_key:
            raise ValueError(f"Pika配置不完整: endpoint={self.endpoint}, api_key={'已设置' if self.api_key else '未设置'}")
    
    def generate_video(self, description, output_path):
        """
        使用Pika Labs API根据描述生成视频
        
        Args:
            description: 视频描述文本
            output_path: 输出视频文件路径
            
        Returns:
            输出视频文件路径
        """
        logger.info(f"使用{self.name}生成视频")
        
        try:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            
            payload = {
                "prompt": description,
                "model": self.model,
                "duration": self.max_duration
            }
            
            # 发送生成请求
            response = requests.post(self.endpoint, headers=headers, json=payload)
            response.raise_for_status()
            
            result = response.json()
            task_id = result.get('taskId')
            
            if not task_id:
                raise ValueError("未能获取视频生成任务ID")
            
            logger.info(f"视频生成任务已提交，任务ID: {task_id}")
            
            # 轮询检查任务状态
            status_url = f"{self.endpoint}/tasks/{task_id}"
            video_url = None
            
            while True:
                status_response = requests.get(status_url, headers=headers)
                status_response.raise_for_status()
                
                status_data = status_response.json()
                status = status_data.get('status')
                
                if status == 'completed':
                    video_url = status_data.get('videoUrl')
                    break
                elif status == 'failed':
                    error_message = status_data.get('error', '未知错误')
                    raise RuntimeError(f"视频生成失败: {error_message}")
                
                logger.info(f"视频生成中，当前状态: {status}")
                time.sleep(5)  # 等待5秒后再次检查
            
            if not video_url:
                raise ValueError("未能获取生成的视频URL")
            
            # 下载视频
            logger.info(f"开始下载生成的视频: {video_url}")
            
            # 确保输出目录存在
            output_dir = os.path.dirname(output_path)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir)
            
            video_response = requests.get(video_url, stream=True)
            video_response.raise_for_status()
            
            with open(output_path, 'wb') as f:
                for chunk in video_response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            logger.info(f"视频已保存: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"生成视频失败: {e}")
            raise

from .qingque_generator import QingqueGenerator

def get_video_generator(config):
    """
    根据配置创建视频生成器
    
    Args:
        config: 视频生成模型配置字典
        
    Returns:
        VideoGenerator实例
    """
    name = config.get('name', '').lower()
    
    if 'runway' in name:
        return RunwayGenerator(config)
    elif 'pika' in name:
        return PikaGenerator(config)
    elif 'qingque' in name or '可灵' in name or 'kling' in name:
        return QingqueGenerator(config)
    else:
        logger.error(f"不支持的视频生成模型类型: {name}")
        raise ValueError(f"不支持的视频生成模型类型: {name}")
