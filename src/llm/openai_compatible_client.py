import requests
import json
import base64
from loguru import logger
from .llm_client import LLMClient

class OpenAICompatibleClient(LLMClient):
    """兼容OpenAI API格式的LLM客户端，可用于调用任何兼容OpenAI API的服务"""
    
    def __init__(self, config):
        """
        初始化兼容OpenAI API的LLM客户端
        
        Args:
            config: LLM配置字典
        """
        super().__init__(config)
        # 额外的配置项
        self.image_format = config.get('image_format', 'base64')  # 图片格式：base64或url
        self.vision_api = config.get('vision_api', True)  # 是否支持视觉API
        self.api_version = config.get('api_version', '')  # API版本，某些兼容服务需要
        self.organization = config.get('organization', '')  # 组织ID，某些服务需要
        
        logger.info(f"初始化兼容OpenAI API的LLM客户端: {self.name}")
    
    def generate_description(self, image_path):
        """
        使用兼容OpenAI API的服务根据图片生成描述
        
        Args:
            image_path: 图片文件路径
            
        Returns:
            生成的描述文本
        """
        logger.info(f"使用{self.name}生成图片描述")
        
        try:
            # 构建请求头
            headers = {
                "Content-Type": "application/json"
            }
            
            # 添加认证信息
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"
            
            # 添加组织ID（如果有）
            if self.organization:
                headers["OpenAI-Organization"] = self.organization
            
            # 添加API版本（如果有）
            if self.api_version:
                headers["OpenAI-Version"] = self.api_version
            
            # 构建消息内容
            messages = [
                {
                    "role": "system",
                    "content": self.system_prompt
                }
            ]
            
            # 根据是否支持视觉API构建不同的用户消息
            if self.vision_api:
                # 读取并编码图片
                with open(image_path, "rb") as image_file:
                    base64_image = base64.b64encode(image_file.read()).decode('utf-8')
                
                # 构建支持视觉的消息格式
                user_message = {
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
            else:
                # 不支持视觉API，只能发送文本
                user_message = {
                    "role": "user",
                    "content": "请生成一段视频脚本或旁白。注意：我本想上传图片，但当前API不支持图片输入。"
                }
                logger.warning(f"{self.name}不支持视觉API，无法处理图片输入")
            
            messages.append(user_message)
            
            # 构建请求体
            payload = {
                "model": self.model,
                "messages": messages,
                "max_tokens": self.max_tokens,
                "temperature": self.temperature
            }
            
            # 发送请求
            response = requests.post(self.endpoint, headers=headers, json=payload)
            response.raise_for_status()
            
            # 解析响应
            result = response.json()
            
            # 提取生成的文本
            # 尝试标准OpenAI格式
            if 'choices' in result and len(result['choices']) > 0:
                if 'message' in result['choices'][0]:
                    description = result['choices'][0]['message']['content']
                elif 'text' in result['choices'][0]:
                    description = result['choices'][0]['text']
                else:
                    raise ValueError(f"无法从响应中提取文本: {result}")
            # 尝试其他可能的格式
            elif 'response' in result:
                description = result['response']
            else:
                raise ValueError(f"无法从响应中提取文本: {result}")
            
            logger.info(f"成功生成描述，长度: {len(description)}")
            return description
            
        except Exception as e:
            logger.error(f"生成描述失败: {e}")
            raise
