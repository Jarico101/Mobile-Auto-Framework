#!/bin/bash
# macOS 环境自动安装脚本

echo "============================================"
echo "  Mobile Automation Framework - macOS Setup"
echo "============================================"
echo ""

# 检查 Homebrew
if ! command -v brew &> /dev/null; then
    echo "❌ Homebrew 未安装，请先安装 Homebrew:"
    echo "   /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
    exit 1
fi

echo "✓ Homebrew 已安装"
echo ""

# 安装系统工具
echo "正在安装系统工具..."
brew install android-platform-tools scrcpy

echo ""
echo "正在安装 Python 依赖..."

# 安装 Python 包
pip install --upgrade pip

pip install \
    adbutils \
    ultralytics \
    paddlepaddle \
    paddleocr \
    transitions \
    label-studio \
    numpy \
    pillow \
    opencv-python \
    pyyaml

echo ""
echo "============================================"
echo "✓ macOS 环境安装完成"
echo "============================================"
echo ""
echo "运行验证: python verify_env.py"
echo ""
