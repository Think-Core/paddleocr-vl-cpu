# PaddleOCR-VL CPU API Server

<div align="center">

[[Python](https://img.shields.io/badge/Python-3.12.3-blue.svg)](https://www.python.org/)
[[FastAPI](https://img.shields.io/badge/FastAPI-0.120.0-green.svg)](https://fastapi.tiangolo.com/)
[[License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[[Model](https://img.shields.io/badge/Model-PaddleOCR--VL--0.9B-orange.svg)](https://www.modelscope.cn/PaddlePaddle/PaddleOCR-VL)

**🎯 Run PaddleOCR-VL on CPU with OpenAI-compatible API**

**在 CPU 上运行 PaddleOCR-VL，提供 OpenAI 兼容 API**

[English](#english) | [简体中文](#chinese)

</div>

---

<a name="english"></a>

## 🌟 Why This Project?

Break the GPU barrier! This project enables you to run PaddleOCR-VL (PaddlePaddle's excellent OCR model) on CPU with an OpenAI-compatible API interface.

| Feature | Official PaddleOCR | This Project |
|---------|-------------------|--------------|
| **CPU Support** | ❌ GPU Required | ✅ Full CPU Support |
| **API Format** | Custom | OpenAI-compatible |
| **Framework** | PaddlePaddle | Pure PyTorch |
| **Streaming** | ❌ | ✅ Real-time streaming |
| **Deployment** | Manual setup | One-line script |
| **Service Management** | Manual | tmux automation |

### ✨ Key Features

- 🖥️ **CPU-Friendly** - Optimized for CPU inference with automatic memory management
- 🔌 **OpenAI-Compatible** - Drop-in replacement for OpenAI's vision API
- 🚀 **Easy Deployment** - One command to install and start
- ⚡ **Streaming Support** - Real-time response streaming
- 💾 **Auto Memory Cleanup** - Prevents memory leaks for long-running services
- 🖼️ **Multiple Formats** - Supports JPEG, PNG, BMP, Base64, and URLs

---

## 🚀 Quick Start

### Prerequisites

- Python 3.12.3
- 16GB+ RAM (recommended for CPU inference)
- Ubuntu/Linux (Windows users please use WSL)

### Installation

```bash
# Clone repository
git clone https://github.com/yourusername/paddleocr-vl-cpu.git
cd paddleocr-vl-cpu

# One-click setup (downloads model automatically ~2GB)
chmod +x quick_init_setup.sh
./quick_init_setup.sh
```

The script will:
1. ✅ Create Python virtual environment
2. ✅ Install all dependencies
3. ✅ Download PaddleOCR-VL-0.9B model (~2GB)
4. ✅ Verify installation

### Start Service

```bash
# Start server
./quick_start.sh start

# Check status
./quick_start.sh status

# View logs
./quick_start.sh attach  # Press Ctrl+B then D to detach

# Stop server
./quick_start.sh stop
```

Server runs on `http://localhost:7777`

---

## 📖 Usage Examples

### Basic OCR

```python
import requests
import base64

# Read and encode image
with open("document.jpg", "rb") as f:
    image_b64 = base64.b64encode(f.read()).decode()

# OCR request
response = requests.post(
    "http://localhost:7777/v1/chat/completions",
    json={
        "model": "paddleocr-vl",
        "messages": [{
            "role": "user",
            "content": [
                {"type": "text", "text": "Extract all text from this image"},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{image_b64}"
                    }
                }
            ]
        }],
        "max_tokens": 2048
    }
)

print(response.json()["choices"][0]["message"]["content"])
```

### Streaming Response

```python
import json

response = requests.post(
    "http://localhost:7777/v1/chat/completions",
    json={
        "model": "paddleocr-vl",
        "messages": [...],  # same as above
        "stream": True
    },
    stream=True
)

for line in response.iter_lines():
    if line:
        line = line.decode('utf-8')
        if line.startswith('data: '):
            data = line[6:]
            if data != '[DONE]':
                chunk = json.loads(data)
                content = chunk["choices"][0]["delta"].get("content", "")
                print(content, end='', flush=True)
```

### cURL Example

```bash
curl -X POST http://localhost:7777/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "paddleocr-vl",
    "messages": [{
      "role": "user",
      "content": [
        {"type": "text", "text": "Read this document"},
        {
          "type": "image_url",
          "image_url": {"url": "data:image/jpeg;base64,/9j/4AAQ..."}
        }
      ]
    }]
  }'
```

---

## 🎯 Use Cases

- 📄 **Document Digitization** - Convert scanned documents to text
- 🧾 **Invoice Processing** - Extract invoice information automatically
- 📋 **Form Recognition** - Parse structured forms and tables
- 🔍 **ID Card Reading** - Extract text from ID cards and certificates
- 📚 **Book Scanning** - Digitize printed books and articles
- 📝 **Handwriting OCR** - Recognize handwritten text (limited accuracy)

---

## ⚠️ Important Notes

### Security Warning

**🔴 This server has NO authentication by default!**

**Do NOT expose directly to the internet!**

For production deployment:
- ✅ Use reverse proxy (Nginx/Caddy) with HTTPS
- ✅ Add API key authentication
- ✅ Configure firewall rules
- ✅ Enable rate limiting
- ✅ Set up monitoring

### Limitations

- ❌ CPU-only (no GPU acceleration in this version)
- ❌ Single request processing (no parallel requests)
- ❌ No built-in authentication
- ❌ Model files (~2GB) not included in repository

---

## 🛠️ Troubleshooting

### Model Download Failed
```bash
# Manual download
mkdir -p models && cd models
git lfs install
git clone https://www.modelscope.cn/PaddlePaddle/PaddleOCR-VL.git PaddleOCR-VL-0.9B
```

### Out of Memory
- Reduce image size
- Lower `max_tokens`
- Restart service: `./quick_start.sh restart`

### Service Won't Start
```bash
# Check port usage
lsof -i :7777

# View logs
./quick_start.sh attach
```

---

## 📁 Project Structure

```
paddleocr-vl-cpu/
├── paddleocr_api.py           # Main API server
├── requirements_frozen.txt    # Locked dependencies
├── quick_init_setup.sh        # Setup script
├── quick_start.sh             # Service management
├── python_version.txt         # Python version lock
└── models/                    # Model files (gitignored)
```

---

## 🙏 Acknowledgments

- **PaddleOCR Team** - For the excellent [PaddleOCR-VL model](https://www.modelscope.cn/PaddlePaddle/PaddleOCR-VL)
- **@hjdhnx** - For inspiration from [this discussion](https://linux.do/t/topic/1054681)
- **FastAPI** - Modern web framework
- **Transformers** - Hugging Face's ML library

---

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

**Note:** PaddleOCR-VL model has its own license. Check the [model repository](https://www.modelscope.cn/PaddlePaddle/PaddleOCR-VL) for details.

---

## 📧 Support

- 🐛 **Bug Reports**: [GitHub Issues](https://github.com/yourusername/paddleocr-vl-cpu/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/yourusername/paddleocr-vl-cpu/discussions)
- ⭐ **Star this project** if you find it helpful!

---

<a name="chinese"></a>

# 中文文档

## 🌟 为什么选择这个项目？

打破 GPU 限制！本项目让你能在 CPU 上运行 PaddleOCR-VL（飞桨团队优秀的 OCR 模型），并提供 OpenAI 兼容的 API 接口。

| 特性 | 官方 PaddleOCR | 本项目 |
|-----|---------------|--------|
| **CPU 支持** | ❌ 需要 GPU | ✅ 完整 CPU 支持 |
| **API 格式** | 自定义 | OpenAI 兼容 |
| **框架依赖** | PaddlePaddle | 纯 PyTorch |
| **流式输出** | ❌ | ✅ 实时流式 |
| **部署方式** | 手动配置 | 一行命令 |
| **服务管理** | 手动管理 | tmux 自动化 |

### ✨ 核心特点

- 🖥️ **CPU 友好** - 针对 CPU 推理优化，自动内存管理
- 🔌 **OpenAI 兼容** - 可直接替换 OpenAI 视觉 API
- 🚀 **快速部署** - 一条命令完成安装和启动
- ⚡ **流式支持** - 实时流式响应
- 💾 **自动清理** - 防止长时间运行的内存泄漏
- 🖼️ **多格式支持** - 支持 JPEG、PNG、BMP、Base64、URL

---

## 🚀 快速开始

### 环境要求

- Python 3.12.3
- 16GB+ 内存（CPU 推理推荐配置）
- Ubuntu/Linux（Windows 用户请使用 WSL）

### 安装

```bash
# 克隆仓库
git clone https://github.com/yourusername/paddleocr-vl-cpu.git
cd paddleocr-vl-cpu

# 一键安装（自动下载模型 约2GB）
chmod +x quick_init_setup.sh
./quick_init_setup.sh
```

脚本会自动完成：
1. ✅ 创建 Python 虚拟环境
2. ✅ 安装所有依赖
3. ✅ 下载 PaddleOCR-VL-0.9B 模型（约 2GB）
4. ✅ 验证安装

### 启动服务

```bash
# 启动服务器
./quick_start.sh start

# 检查状态
./quick_start.sh status

# 查看日志
./quick_start.sh attach  # 按 Ctrl+B 然后 D 退出

# 停止服务
./quick_start.sh stop
```

服务运行在 `http://localhost:7777`

---

## 📖 使用示例

### 基础 OCR

```python
import requests
import base64

# 读取并编码图片
with open("document.jpg", "rb") as f:
    image_b64 = base64.b64encode(f.read()).decode()

# OCR 请求
response = requests.post(
    "http://localhost:7777/v1/chat/completions",
    json={
        "model": "paddleocr-vl",
        "messages": [{
            "role": "user",
            "content": [
                {"type": "text", "text": "识别这张图片中的所有文字"},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{image_b64}"
                    }
                }
            ]
        }],
        "max_tokens": 2048
    }
)

print(response.json()["choices"][0]["message"]["content"])
```

### 流式响应

```python
import json

response = requests.post(
    "http://localhost:7777/v1/chat/completions",
    json={
        "model": "paddleocr-vl",
        "messages": [...],  # 同上
        "stream": True
    },
    stream=True
)

for line in response.iter_lines():
    if line:
        line = line.decode('utf-8')
        if line.startswith('data: '):
            data = line[6:]
            if data != '[DONE]':
                chunk = json.loads(data)
                content = chunk["choices"][0]["delta"].get("content", "")
                print(content, end='', flush=True)
```

### cURL 示例

```bash
curl -X POST http://localhost:7777/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "paddleocr-vl",
    "messages": [{
      "role": "user",
      "content": [
        {"type": "text", "text": "识别文字"},
        {
          "type": "image_url",
          "image_url": {"url": "data:image/jpeg;base64,/9j/4AAQ..."}
        }
      ]
    }]
  }'
```

---

## 🎯 应用场景

- 📄 **文档数字化** - 将扫描文档转换为文本
- 🧾 **发票处理** - 自动提取发票信息
- 📋 **表单识别** - 解析结构化表单和表格
- 🔍 **证件识别** - 提取身份证、证书等文字
- 📚 **书籍扫描** - 数字化纸质书籍和文章
- 📝 **手写识别** - 识别手写文字（准确度有限）

---

## ⚠️ 重要提示

### 安全警告

**🔴 服务器默认无身份验证！**

**切勿直接暴露到公网！**

生产部署建议：
- ✅ 使用反向代理（Nginx/Caddy）配置 HTTPS
- ✅ 添加 API 密钥验证
- ✅ 配置防火墙规则
- ✅ 启用速率限制
- ✅ 设置监控告警

### 限制说明

- ❌ 仅支持 CPU（本版本不含 GPU 加速）
- ❌ 单次请求处理（不支持并发请求）
- ❌ 无内置身份验证
- ❌ 模型文件（约 2GB）不包含在仓库中

---

## 🛠️ 故障排除

### 模型下载失败
```bash
# 手动下载
mkdir -p models && cd models
git lfs install
git clone https://www.modelscope.cn/PaddlePaddle/PaddleOCR-VL.git PaddleOCR-VL-0.9B
```

### 内存不足
- 压缩图片尺寸
- 降低 `max_tokens`
- 重启服务：`./quick_start.sh restart`

### 服务无法启动
```bash
# 检查端口占用
lsof -i :7777

# 查看日志
./quick_start.sh attach
```

---

## 📁 项目结构

```
paddleocr-vl-cpu/
├── paddleocr_api.py           # API 服务器主程序
├── requirements_frozen.txt    # 锁定的依赖版本
├── quick_init_setup.sh        # 安装脚本
├── quick_start.sh             # 服务管理脚本
├── python_version.txt         # Python 版本锁定
└── models/                    # 模型文件（已忽略）
```

---

## 🙏 致谢

- **PaddleOCR 团队** - 提供出色的 [PaddleOCR-VL 模型](https://www.modelscope.cn/PaddlePaddle/PaddleOCR-VL)
- **@hjdhnx** - 来自 [这个讨论](https://linux.do/t/topic/1054681) 的启发
- **FastAPI** - 现代化 Web 框架
- **Transformers** - Hugging Face 的 ML 库

---

## 📄 许可证

MIT 许可证 - 详见 [LICENSE](LICENSE) 文件。

**注意：** PaddleOCR-VL 模型有自己的许可证，请查看 [模型仓库](https://www.modelscope.cn/PaddlePaddle/PaddleOCR-VL) 了解详情。

---

## 📧 支持

- 🐛 **错误报告**：[GitHub Issues](https://github.com/yourusername/paddleocr-vl-cpu/issues)
- 💬 **问题讨论**：[GitHub Discussions](https://github.com/yourusername/paddleocr-vl-cpu/discussions)
- ⭐ **觉得有用请点星！**

---

<div align="center">

**Made with ❤️ for the OCR community**

**用 ❤️ 为 OCR 社区打造**

[⭐ Star](https://github.com/yourusername/paddleocr-vl-cpu) · [🐛 Report Bug](https://github.com/yourusername/paddleocr-vl-cpu/issues) · [💡 Request Feature](https://github.com/yourusername/paddleocr-vl-cpu/issues)

</div>
