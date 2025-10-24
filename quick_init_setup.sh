#!/bin/bash

echo "=== PaddleOCR-VL 快速环境部署脚本 ==="

# 创建虚拟环境
echo "1. 创建虚拟环境..."
Python3.12.3 -m venv paddleocrvl
source paddleocrvl/bin/activate

# 安装所有包
echo "2. 安装 Python 依赖..."
pip install --upgrade pip
pip install -r requirements_frozen.txt

# 确保 git lfs 已安装
echo "3. 检查 Git LFS..."
if ! command -v git-lfs &> /dev/null; then
    echo "安装 Git LFS..."
    sudo apt-get update && sudo apt-get install -y git-lfs
fi
git lfs install

# 下载模型
echo "4. 下载 PaddleOCR-VL 模型..."
mkdir -p models
cd models

if [ -d "PaddleOCR-VL" ]; then
    echo "模型目录已存在，跳过下载"
else
    # 使用官方提供的 git clone 地址
    git clone https://www.modelscope.cn/PaddlePaddle/PaddleOCR-VL.git
fi

cd ..

echo "=== 环境部署完成 ==="
echo "模型位置: $(pwd)/models/PaddleOCR-VL"
