import requests
import json
import time
import os
import jwt
from datetime import datetime
from loguru import logger

class QingqueGenerator:
    """可灵(Qingque/Kling)视频生成API客户端"""
    
    def __init__(self, config):
        """
        初始化可灵视频生成器
        
        Args:
            config: 视频生成模型配置字典
        """
        self.config = config
        self.name = config.get('name', 'Qingque')
        self.endpoint = config.get('endpoint', 'https://api.klingai.com')
        self.access_key = config.get('access_key')
        self.secret_key = config.get('secret_key')
        self.model = config.get('model', 'kling-v1')
        self.max_duration = config.get('max_duration', 5)  # 默认5秒
        
        if not self.access_key or not self.secret_key:
            raise ValueError(f"可灵API配置不完整: access_key={'已设置' if self.access_key else '未设置'}, secret_key={'已设置' if self.secret_key else '未设置'}")
    
    def _generate_jwt_token(self):
        """
        生成JWT Token用于API认证
        
        Returns:
            JWT Token字符串
        """
        headers = {
            "alg": "HS256",
            "typ": "JWT"
        }
        
        payload = {
            "iss": self.access_key,
            "exp": int(time.time()) + 1800,  # 有效时间30分钟
            "nbf": int(time.time()) - 5  # 开始生效时间为当前时间-5秒
        }
        
        token = jwt.encode(payload, self.secret_key, headers=headers)
        return token
    
    def generate_video(self, description, output_path):
        """
        使用可灵API根据描述生成视频
        
        Args:
            description: 视频描述文本
            output_path: 输出视频文件路径
            
        Returns:
            输出视频文件路径
        """
        logger.info(f"使用{self.name}生成视频")
        
        try:
            # 生成JWT Token
            jwt_token = self._generate_jwt_token()
            
            # 设置请求头
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {jwt_token}"
            }
            
            # 构建请求体
            payload = {
                "model_name": self.model,
                "prompt": description,
                "negative_prompt": "",
                "cfg_scale": 0.5,
                "mode": "std",
                "aspect_ratio": "16:9",
                "duration": str(self.max_duration)
            }
            
            # 发送生成请求
            url = f"{self.endpoint}/v1/videos/text2video"
            logger.info(f"发送视频生成请求: {url}")
            
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            
            result = response.json()
            
            # 检查API响应
            if result.get('code') != 0:
                error_message = result.get('message', '未知错误')
                raise RuntimeError(f"视频生成请求失败: {error_message}")
            
            task_id = result.get('data', {}).get('task_id')
            
            if not task_id:
                raise ValueError("未能获取视频生成任务ID")
            
            logger.info(f"视频生成任务已提交，任务ID: {task_id}")
            
            # 轮询检查任务状态
            video_url = self._poll_task_status(task_id)
            
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
    
    def _poll_task_status(self, task_id):
        """
        轮询检查任务状态
        
        Args:
            task_id: 任务ID
            
        Returns:
            视频URL或None
        """
        # 查询任务状态的API路径
        status_path = f"/v1/videos/text2video/{task_id}"
        
        while True:
            # 生成新的JWT Token
            jwt_token = self._generate_jwt_token()
            
            # 更新请求头
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {jwt_token}"
            }
            
            status_url = f"{self.endpoint}{status_path}"
            status_response = requests.get(status_url, headers=headers)
            status_response.raise_for_status()
            
            status_data = status_response.json()
            
            # 检查API响应
            if status_data.get('code') != 0:
                error_message = status_data.get('message', '未知错误')
                raise RuntimeError(f"查询任务状态失败: {error_message}")
            
            task_info = status_data.get('data', {})
            status = task_info.get('task_status')
            
            logger.info(f"视频生成中，当前状态: {status}")
            
            if status == 'succeed':
                # 任务成功，获取视频URL
                task_result = task_info.get('task_result', {})
                videos = task_result.get('videos', [])
                
                if videos and len(videos) > 0:
                    video_url = videos[0].get('url')
                    video_duration = videos[0].get('duration')
                    logger.info(f"视频生成成功，时长: {video_duration}秒，URL: {video_url}")
                    return video_url
                else:
                    raise ValueError("任务成功但未找到视频URL")
            elif status == 'failed':
                # 任务失败
                error_message = task_info.get('task_status_msg', '未知错误')
                raise RuntimeError(f"视频生成失败: {error_message}")
            elif status in ['submitted', 'processing']:
                # 任务仍在处理中，等待后再次查询
                logger.info(f"任务正在处理中，状态: {status}")
                time.sleep(5)  # 等待5秒后再次检查
            else:
                # 未知状态
                raise RuntimeError(f"未知的任务状态: {status}")
