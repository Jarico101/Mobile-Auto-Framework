@echo off
REM Windows 环境自动安装脚本
chcp 65001 >nul

echo ============================================
echo   Mobile Automation Framework - Windows Setup
echo ============================================
echo.

echo 正在安装 Python 依赖...
echo.

REM 升级 pip
python -m pip install --upgrade pip

REM 安装依赖（使用清华镜像加速）
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple ^
    adbutils ^
    ultralytics ^
    paddlepaddle ^
    paddleocr ^
    transitions ^
    label-studio ^
    numpy ^
    pillow ^
    opencv-python ^
    pyyaml

echo.
echo ============================================
echo Python 依赖安装完成
echo ============================================
echo.
echo 请手动安装以下工具：
echo.
echo 1. ADB platform-tools
echo    下载地址: https://developer.android.com/studio/releases/platform-tools
echo    解压后添加到系统 PATH
echo.
echo 2. scrcpy（投屏工具）
echo    下载地址: https://github.com/Genymobile/scrcpy/releases
echo    解压后添加到系统 PATH
echo.
echo ============================================
echo 运行验证: python verify_env.py
echo ============================================

pause
