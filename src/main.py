#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import argparse
import time
import glob
import random
from loguru import logger

from utils.config import Config
from utils.logger import setup_logger
from utils.image_utils import load_image, resize_image
from llm.llm_client import get_llm_client
from video.video_generator import get_video_generator

def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description='图片转视频生成器')
    parser.add_argument('--image', '-i', help='输入图片路径')
    parser.add_argument('--output', '-o', help='输出视频路径')
    parser.add_argument('--llm', help='使用的LLM提供商名称')
    parser.add_argument('--video-model', help='使用的视频生成模型提供商名称')
    parser.add_argument('--config', '-c', help='配置文件路径')
    parser.add_argument('--save-description', '-s', help='保存生成的描述文本到文件')
    parser.add_argument('--list-providers', '-l', action='store_true', help='列出所有可用的提供商')
    return parser.parse_args()

def get_default_image():
    """
    获取默认图片路径
    
    如果项目的images目录中有图片，则随机选择一张
    
    Returns:
        图片路径或None
    """
    # 获取项目根目录
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    images_dir = os.path.join(root_dir, 'images')
    
    # 检查images目录是否存在
    if not os.path.exists(images_dir):
        logger.warning(f"默认图片目录不存在: {images_dir}")
        return None
    
    # 获取所有图片文件
    image_extensions = ['*.jpg', '*.jpeg', '*.png', '*.gif', '*.bmp', '*.webp']
    image_files = []
    
    for ext in image_extensions:
        image_files.extend(glob.glob(os.path.join(images_dir, ext)))
        image_files.extend(glob.glob(os.path.join(images_dir, ext.upper())))
    
    if not image_files:
        logger.warning(f"默认图片目录中没有图片: {images_dir}")
        return None
    
    # 随机选择一张图片
    selected_image = random.choice(image_files)
    logger.info(f"使用默认图片: {selected_image}")
    return selected_image

def main():
    """主函数"""
    # 解析命令行参数
    args = parse_args()
    
    # 加载配置
    config = Config(args.config)
    
    # 设置日志
    setup_logger(config.get_logging_config())
    
    # 如果只是列出提供商，则显示后退出
    if args.list_providers:
        llm_providers = config.get_available_llm_providers()
        video_generators = config.get_available_video_generators()
        
        print("可用的LLM提供商:")
        for provider in llm_providers:
            print(f"  - {provider}")
        
        print("\n可用的视频生成模型提供商:")
        for provider in video_generators:
            print(f"  - {provider}")
        
        return
    
    # 检查输入图片
    if not args.image:
        # 如果未指定输入图片，则使用默认图片
        args.image = get_default_image()
        
        if not args.image:
            logger.error("未指定输入图片，且未找到默认图片")
            print("错误: 请指定输入图片路径，或在项目的images目录中放置图片")
            return
    
    # 检查输入图片是否存在
    if not os.path.exists(args.image):
        logger.error(f"输入图片不存在: {args.image}")
        print(f"错误: 输入图片不存在: {args.image}")
        return
    
    # 设置输出视频路径
    if not args.output:
        # 如果未指定输出路径，则使用输入图片的路径和名称，但扩展名改为.mp4
        base_name = os.path.splitext(args.image)[0]
        args.output = f"{base_name}_video.mp4"
    
    # 获取LLM配置
    llm_config = config.get_llm_config(args.llm)
    
    # 获取视频生成模型配置
    video_config = config.get_video_generator_config(args.video_model)
    
    try:
        # 步骤1: 加载并处理图片
        logger.info(f"正在处理图片: {args.image}")
        image = load_image(args.image)
        image = resize_image(image)
        
        # 步骤2: 使用LLM生成描述
        logger.info(f"使用{llm_config['name']}生成描述")
        llm_client = get_llm_client(llm_config)
        start_time = time.time()
        description = llm_client.generate_description(args.image)
        end_time = time.time()
        logger.info(f"描述生成完成，用时: {end_time - start_time:.2f}秒")
        
        # 如果需要，保存描述文本
        if args.save_description:
            with open(args.save_description, 'w', encoding='utf-8') as f:
                f.write(description)
            logger.info(f"描述已保存到: {args.save_description}")
        
        # 步骤3: 使用视频生成模型生成视频
        logger.info(f"使用{video_config['name']}生成视频")
        video_generator = get_video_generator(video_config)
        start_time = time.time()
        output_path = video_generator.generate_video(description, args.output)
        end_time = time.time()
        logger.info(f"视频生成完成，用时: {end_time - start_time:.2f}秒")
        
        logger.info(f"处理完成！视频已保存到: {output_path}")
        
    except Exception as e:
        logger.error(f"处理过程中出错: {e}")
        raise

if __name__ == "__main__":
    main()
