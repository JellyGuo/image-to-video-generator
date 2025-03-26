# Image to Video Generator

这个项目使用LLM（大型语言模型）将图片转换为视频。处理流程包括两个主要步骤：

1. **图生文**：上传图片到LLM，生成视频内容的脚本、旁白或描述
2. **文生视频**：将第一步生成的文本描述输入到视频生成模型中，创建最终视频

## 功能特点

- 支持通过HTTP/HTTPS调用不同的LLM
- 支持配置模型endpoint和API密钥
- 支持在不同LLM之间切换
- 支持自定义系统提示(System Prompt)
- 命令行界面操作简单
- **默认使用可灵(Qingque)视频生成API**
- **支持OpenAI API兼容的LLM服务**
- **支持自动使用项目images目录中的图片**

## 安装与使用

请参考下面的说明安装和使用本项目。

### 安装依赖

```bash
pip install -r requirements.txt
```

### 配置

在使用前，请在`config/config.yaml`中配置您的LLM API密钥和端点。项目已默认配置可灵(Qingque)视频生成API。

### 准备图片

您可以将图片放在项目的`images`目录中，如果不指定输入图片，程序将随机选择该目录中的一张图片。

### 运行

```bash
# 指定输入图片
python src/main.py --image path/to/image.jpg --output path/to/output.mp4

# 使用默认图片目录中的图片
python src/main.py --output path/to/output.mp4
```

### 列出可用的提供商

```bash
python src/main.py --list-providers
```

### 指定使用的LLM和视频生成模型

```bash
python src/main.py --image path/to/image.jpg --llm llm1 --video-model qingque
```

## 项目结构

```
image_to_video_generator/
├── config/             # 配置文件
├── images/             # 默认图片目录
├── logs/               # 日志文件
├── src/                # 源代码
│   ├── llm/            # LLM相关代码
│   ├── video/          # 视频生成相关代码
│   ├── utils/          # 工具函数
│   └── main.py         # 命令行入口
└── README.md           # 项目说明
```

## 支持的LLM

1. **OpenAI** - 支持GPT-4 Vision等模型
2. **Claude** - 支持Claude 3 Opus等模型
3. **OpenAI API兼容服务** - 支持任何兼容OpenAI API的服务，如：
   - 本地部署的开源模型
   - Ollama
   - 其他云服务提供商的兼容API

## 支持的视频生成模型

1. **可灵(Qingque)** - 默认视频生成模型
2. **Runway Gen-2**
3. **Pika Labs**
