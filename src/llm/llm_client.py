import requests
import json
import base64
from abc import ABC, abstractmethod
from loguru import logger
from .openai_compatible_client import OpenAICompatibleClient

class LLMClient(ABC):
    """LLM客户端抽象基类"""
    
    def __init__(self, config):
        """
        初始化LLM客户端
        
        Args:
            config: LLM配置字典
        """
        self.config = config
        self.name = config.get('name', 'Unknown LLM')
        self.endpoint = config.get('endpoint')
        self.api_key = config.get('api_key')
        self.model = config.get('model')
        self.max_tokens = config.get('max_tokens', 1000)
        self.temperature = config.get('temperature', 0.7)
        self.system_prompt = config.get('system_prompt', '')
        
        if not self.endpoint or not self.api_key:
            raise ValueError(f"LLM配置不完整: endpoint={self.endpoint}, api_key={'已设置' if self.api_key else '未设置'}")
    
    @abstractmethod
    def generate_description(self, image_path):
        """
        根据图片生成描述
        
        Args:
            image_path: 图片文件路径
            
        Returns:
            生成的描述文本
        """
        pass

class OpenAIClient(LLMClient):
    """OpenAI API客户端"""
    
    def generate_description(self, image_path):
        """
        使用OpenAI API根据图片生成描述
        
        Args:
            image_path: 图片文件路径
            
        Returns:
            生成的描述文本
        """
        logger.info(f"使用{self.name}生成图片描述")
        
        try:
            # 读取并编码图片
            with open(image_path, "rb") as image_file:
                base64_image = base64.b64encode(image_file.read()).decode('utf-8')
            
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            
            payload = {
                "model": self.model,
                "messages": [
                    {
                        "role": "system",
                        "content": self.system_prompt
                    },
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "请根据这张图片生成一段视频脚本或旁白。"
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                "max_tokens": self.max_tokens,
                "temperature": self.temperature
            }
            
            response = requests.post(self.endpoint, headers=headers, json=payload)
            response.raise_for_status()
            
            result = response.json()
            description = result['choices'][0]['message']['content']
            
            logger.info(f"成功生成描述，长度: {len(description)}")
            return description
            
        except Exception as e:
            logger.error(f"生成描述失败: {e}")
            raise

class ClaudeClient(LLMClient):
    """Anthropic Claude API客户端"""
    
    def generate_description(self, image_path):
        """
        使用Claude API根据图片生成描述
        
        Args:
            image_path: 图片文件路径
            
        Returns:
            生成的描述文本
        """
        logger.info(f"使用{self.name}生成图片描述")
        
        try:
            # 读取并编码图片
            with open(image_path, "rb") as image_file:
                base64_image = base64.b64encode(image_file.read()).decode('utf-8')
            
            headers = {
                "Content-Type": "application/json",
                "x-api-key": self.api_key,
                "anthropic-version": "2023-06-01"
            }
            
            payload = {
                "model": self.model,
                "system": self.system_prompt,
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "请根据这张图片生成一段视频脚本或旁白。"
                            },
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": "image/jpeg",
                                    "data": base64_image
                                }
                            }
                        ]
                    }
                ],
                "max_tokens": self.max_tokens,
                "temperature": self.temperature
            }
            
            response = requests.post(self.endpoint, headers=headers, json=payload)
            response.raise_for_status()
            
            result = response.json()
            description = result['content'][0]['text']
            
            logger.info(f"成功生成描述，长度: {len(description)}")
            return description
            
        except Exception as e:
            logger.error(f"生成描述失败: {e}")
            raise

def get_llm_client(config):
    """
    根据配置创建LLM客户端
    
    Args:
        config: LLM配置字典
        
    Returns:
        LLMClient实例
    """
    name = config.get('name', '').lower()
    
    if 'compatible' in name or 'openai-api-compatible' in name:
        return OpenAICompatibleClient(config)
    elif 'openai' in name:
        return OpenAIClient(config)
    elif 'claude' in name or 'anthropic' in name:
        return ClaudeClient(config)
    else:
        logger.error(f"不支持的LLM类型: {name}")
        raise ValueError(f"不支持的LLM类型: {name}")
