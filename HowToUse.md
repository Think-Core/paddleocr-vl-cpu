# PaddleOCR-VL API 服务

基于 PaddleOCR-VL 模型的 OCR 识别 API 服务，提供兼容 OpenAI 格式的接口，支持图片文字识别和文档解析。

## 📋 系统要求

- **Python**: 3.12.3
- **系统**: Linux (推荐 Ubuntu 20.04+)
- **内存**: 建议 16GB+ (模型加载约需 8-10GB)
- **磁盘**: 至少 20GB 可用空间
- **依赖**: Git, Git LFS, tmux

## 🚀 快速开始

### 1. 下载项目

```bash
mkdir paddleocr-vl-dev [项目文件夹]
cd paddleocr-vl-dev
```

### 2. 一键部署环境

```bash
# 给脚本添加执行权限
chmod +x quick_init_setup.sh

# 运行环境初始化脚本（自动安装依赖和下载模型）
./quick_init_setup.sh
```

此脚本会自动：
- ✅ 创建 Python 虚拟环境 `paddleocrvl`
- ✅ 安装所有必要的 Python 包
- ✅ 配置 Git LFS
- ✅ 下载 PaddleOCR-VL 模型（约 3.8GB）

### 3. 修改模型路径

编辑 `paddleocr_api.py`，将模型路径修改为你的实际路径：

```python
LOCAL_PATH = "/your/path/paddleocr-vl-dev/models/PaddleOCR-VL"  # 修改为实际路径
```

或使用 sed 命令自动修改：
```bash
sed -i "s|/root/paddleocr-vl/models/PaddleOCR-VL|$(pwd)/models/PaddleOCR-VL|g" paddleocr_api.py
```

### 4. 启动服务

使用 tmux 管理服务（推荐）：

```bash
# 启动服务
./quick_start.sh start

# 查看服务状态
./quick_start.sh status

# 查看服务日志
./quick_start.sh attach
# (退出查看: Ctrl+B, 然后按 D)
```

服务启动后会监听在 `http://0.0.0.0:7777`

## 📡 API 使用

### 接口地址

- **聊天接口**: `http://[服务器IP]:7777/v1/chat/completions`
- **模型列表**: `http://[服务器IP]:7777/v1/models`

### 请求示例

#### Python 示例

```python
import requests
import base64

def ocr_image(image_path, prompt="识别图片中的所有文字"):
    # 读取图片并转base64
    with open(image_path, 'rb') as f:
        image_base64 = base64.b64encode(f.read()).decode('utf-8')
    
    # 构建请求
    url = "http://localhost:7777/v1/chat/completions"
    data = {
        "model": "paddleocr-vl",
        "messages": [{
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}
                }
            ]
        }],
        "max_tokens": 4096,
        "temperature": 0.7,
        "stream": False
    }
    
    # 发送请求
    response = requests.post(url, json=data)
    result = response.json()
    
    # 提取识别结果
    return result['choices'][0]['message']['content']

# 使用示例
text = ocr_image("test.jpg", "请识别并整理图片中的文字")
print(text)
```

#### cURL 示例

```bash
curl -X POST http://localhost:7777/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "paddleocr-vl",
    "messages": [{
      "role": "user",
      "content": "识别图片中的文字"
    }],
    "max_tokens": 4096,
    "stream": false
  }'
```

### 支持的参数

| 参数 | 类型 | 默认值 | 说明 |
|-----|------|--------|------|
| `model` | string | - | 模型名称，使用 "paddleocr-vl" |
| `messages` | array | - | 消息数组，支持文本和图片 |
| `max_tokens` | integer | 131072 | 最大生成 token 数 |
| `temperature` | float | 0.7 | 生成温度，0-1之间 |
| `stream` | boolean | false | 是否流式返回 |

## 🛠️ 服务管理

### 使用 tmux 管理脚本

```bash
# 启动服务
./quick_start.sh start

# 停止服务
./quick_start.sh stop

# 重启服务
./quick_start.sh restart

# 查看服务（连接到tmux会话）
./quick_start.sh attach

# 检查服务状态
./quick_start.sh status
```

### 手动管理

```bash
# 激活虚拟环境
source paddleocrvl/bin/activate

# 直接运行
python paddleocr_api.py

# 或使用 tmux
tmux new -s paddleocr-api
source paddleocrvl/bin/activate
python paddleocr_api.py
# Ctrl+B, D 退出tmux
```

## 📁 项目结构

```
paddleocr-vl-dev/
├── paddleocr_api.py          # API 服务主程序
├── requirements_frozen.txt    # Python 依赖包列表
├── quick_init_setup.sh       # 环境初始化脚本
├── quick_start.sh            # tmux 服务管理脚本
├── python_version.txt        # Python 版本记录
├── README.md                 # 项目文档
├── paddleocrvl/             # Python 虚拟环境（运行setup后生成）
└── models/                   # 模型文件目录（运行setup后生成）
    └── PaddleOCR-VL/        # PaddleOCR-VL 模型文件
```

## 🔧 常见问题

### 1. 内存不足

如果遇到内存错误，可以尝试：
- 使用 float16 精度（已在代码中自动尝试）
- 增加系统 swap 空间
- 减小 `max_tokens` 参数值

### 2. 端口被占用

```bash
# 查看端口占用
lsof -i:7777

# 修改端口（编辑 paddleocr_api.py 最后一行）
uvicorn.run(app, host="0.0.0.0", port=8888)  # 改为其他端口
```

### 3. 模型下载失败

如果自动下载失败，可以手动下载：

```bash
cd models
# 使用 Git LFS
git clone https://www.modelscope.cn/PaddlePaddle/PaddleOCR-VL.git

# 或使用 ModelScope CLI
pip install modelscope
modelscope download --model PaddlePaddle/PaddleOCR-VL --local_dir ./PaddleOCR-VL
```

### 4. tmux 会话管理

```bash
# 列出所有会话
tmux ls

# 强制关闭会话
tmux kill-session -t paddleocr-api

# 关闭所有会话
tmux kill-server
```

## 🌟 功能特点

- ✅ **兼容 OpenAI API 格式**：可直接替换 OpenAI 接口地址使用
- ✅ **支持多种图片格式**：JPEG、PNG、BMP 等
- ✅ **支持 Base64 和 URL**：图片可以是 Base64 编码或网络地址
- ✅ **流式输出**：支持实时返回识别结果
- ✅ **自动内存管理**：处理完成后自动释放内存
- ✅ **CPU 运行优化**：支持 float16 精度，降低内存占用


## 🔄 更新部署

当需要在新机器上部署时：

1. 复制整个项目文件夹
2. 运行 `./quick_init_setup.sh` 初始化环境
3. 修改 `paddleocr_api.py` 中的模型路径
4. 运行 `./quick_start.sh start` 启动服务

