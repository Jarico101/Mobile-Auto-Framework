# 环境安装指南 - 跨平台（macOS + Windows）

## 前置要求

- Python 3.8+
- Git

---

## 1. ADB 控制

### Python 包
```bash
pip install adbutils
```

### ADB 工具本体

**macOS:**
```bash
brew install android-platform-tools
```

**Windows:**
1. 下载 [platform-tools](https://developer.android.com/studio/releases/platform-tools)
2. 解压到 `C:\platform-tools`
3. 添加到系统 PATH：
   - 右键"此电脑" → 属性 → 高级系统设置 → 环境变量
   - 在"系统变量"中找到 `Path`，编辑
   - 添加 `C:\platform-tools`

**验证安装:**
```bash
adb version
```

---

## 2. YOLO 目标检测

### 安装 YOLOv8
```bash
pip install ultralytics
```

**验证安装:**
```bash
python -c "from ultralytics import YOLO; print('YOLOv8 OK')"
```

---

## 3. OCR 文字识别

### PaddleOCR

**macOS:**
```bash
pip install paddlepaddle paddleocr
```

**Windows:**
```bash
# CPU 版本
pip install paddlepaddle paddleocr

# GPU 版本（如果有NVIDIA显卡）
pip install paddlepaddle-gpu paddleocr
```

**验证安装:**
```bash
python -c "from paddleocr import PaddleOCR; print('PaddleOCR OK')"
```

---

## 4. FSM 状态机

```bash
pip install transitions
```

**验证安装:**
```bash
python -c "from transitions import Machine; print('transitions OK')"
```

---

## 5. 标注工具

### Label Studio (推荐)

```bash
pip install label-studio
```

**启动:**
```bash
label-studio
```
浏览器自动打开 `http://localhost:8080`

### CVAT (备选)

**macOS / Windows:**
使用 Docker 安装：
```bash
docker run -it --rm -p 8080:8080 cvat/server
```

---

## 6. 投屏调试工具

### scrcpy

**macOS:**
```bash
brew install scrcpy
```

**Windows:**
1. 下载 [scrcpy releases](https://github.com/Genymobile/scrcpy/releases)
2. 解压到任意目录（如 `C:\scrcpy`）
3. 添加到系统 PATH（同ADB方法）

**验证安装:**
```bash
scrcpy --version
```

**使用:**
```bash
# 手机连接后直接运行
scrcpy
```

---

## 7. 其他依赖

### 基础库
```bash
pip install numpy pillow opencv-python pyyaml
```

---

## 完整安装脚本

### macOS
创建 `setup_mac.sh`:
```bash
#!/bin/bash

# 安装 Homebrew 工具
brew install android-platform-tools scrcpy

# 安装 Python 依赖
pip install adbutils \
    ultralytics \
    paddlepaddle \
    paddleocr \
    transitions \
    label-studio \
    numpy \
    pillow \
    opencv-python \
    pyyaml

echo "✓ macOS 环境安装完成"
```

运行:
```bash
chmod +x setup_mac.sh
./setup_mac.sh
```

---

### Windows
创建 `setup_windows.bat`:
```batch
@echo off
echo ============================================
echo Windows 环境安装
echo ============================================
echo.

REM 安装 Python 依赖
pip install adbutils ^
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
echo 1. ADB platform-tools
echo    https://developer.android.com/studio/releases/platform-tools
echo 2. scrcpy
echo    https://github.com/Genymobile/scrcpy/releases
echo.
echo 安装后记得添加到系统 PATH
echo ============================================

pause
```

运行:
```batch
setup_windows.bat
```

---

## 验证安装

创建 `verify_env.py`:
```python
#!/usr/bin/env python3
"""验证环境安装"""

def check_import(module_name, import_name=None):
    """检查模块是否可导入"""
    if import_name is None:
        import_name = module_name
    
    try:
        __import__(import_name)
        print(f"✓ {module_name}")
        return True
    except ImportError:
        print(f"✗ {module_name} - 未安装")
        return False

def check_command(cmd):
    """检查命令是否可用"""
    import subprocess
    try:
        result = subprocess.run([cmd, '--version'], 
                              capture_output=True, 
                              timeout=5)
        if result.returncode == 0:
            print(f"✓ {cmd}")
            return True
        else:
            print(f"✗ {cmd} - 未安装")
            return False
    except:
        print(f"✗ {cmd} - 未安装")
        return False

print("=" * 50)
print("环境检查")
print("=" * 50)

print("\nPython 包:")
results = []
results.append(check_import("adbutils"))
results.append(check_import("ultralytics"))
results.append(check_import("paddleocr"))
results.append(check_import("transitions"))
results.append(check_import("label_studio", "label_studio"))
results.append(check_import("numpy"))
results.append(check_import("PIL", "pillow"))
results.append(check_import("cv2", "opencv-python"))

print("\n系统工具:")
results.append(check_command("adb"))
results.append(check_command("scrcpy"))

print("\n" + "=" * 50)
passed = sum(results)
total = len(results)
print(f"结果: {passed}/{total} 通过")
print("=" * 50)
```

运行验证:
```bash
python verify_env.py
```

---

## 常见问题

### Q: Windows上pip install很慢
A: 使用国内镜像源
```bash
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple <package>
```

### Q: PaddleOCR 导入报错
A: 尝试降级 protobuf
```bash
pip install protobuf==3.20.0
```

### Q: scrcpy 无法连接
A: 
1. 确认 ADB 已连接: `adb devices`
2. 确认手机开启USB调试
3. 尝试重启 ADB: `adb kill-server && adb start-server`

### Q: macOS M1/M2 芯片兼容性
A: PaddlePaddle 需要使用特定版本
```bash
pip install paddlepaddle==2.4.2
```

---

## 推荐安装顺序

1. ✅ ADB 工具（adbutils + platform-tools）
2. ✅ scrcpy（投屏调试）
3. ✅ YOLOv8（ultralytics）
4. ✅ PaddleOCR
5. ✅ transitions（状态机）
6. ✅ Label Studio（标注工具）
7. ✅ 验证环境（运行 verify_env.py）

---

## 下一步

环境安装完成后：
1. 运行 `python verify_env.py` 验证
2. 运行 `python tests/test_device.py` 测试设备连接
3. 开始数据采集和模型训练
