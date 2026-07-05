# 快速开始指南

## 环境准备

### 1. 安装ADB

**Windows:**
```bash
# 下载 platform-tools
https://developer.android.com/studio/releases/platform-tools

# 解压后将目录添加到系统PATH
```

**macOS:**
```bash
brew install android-platform-tools
```

**Linux:**
```bash
sudo apt-get install android-tools-adb
```

验证安装：
```bash
adb version
```

### 2. 手机设置

1. 打开「开发者选项」
   - 设置 → 关于手机 → 连续点击「版本号」7次
2. 开启「USB调试」
3. 连接电脑，手机上允许USB调试授权

### 3. 安装Python依赖

```bash
cd mobile-auto-framework
pip install -r requirements.txt
```

## 快速测试

### 1. 测试设备连接

```bash
python tests/test_device.py
```

预期输出：
```
✓ 设备连接成功
✓ 屏幕尺寸: 1080 x 1920
✓ 截图成功
```

### 2. 单独测试各模块

**设备层:**
```bash
python src/device/device_controller.py
```

**截图层:**
```bash
python src/capture/screen_capture.py
```

**感知层（需要YOLO模型）:**
```bash
python src/perception/perception_engine.py
```

**规则引擎:**
```bash
python src/rules/rule_engine.py
```

## 数据集准备

### 方案B：录屏提取（推荐）

1. **录制游戏视频**
   ```bash
   # 手机开启录屏，游玩30分钟
   # 或通过ADB录屏：
   adb shell screenrecord /sdcard/gameplay.mp4
   
   # 拉取到电脑
   adb pull /sdcard/gameplay.mp4 data/videos/
   ```

2. **提取视频帧**
   ```bash
   python scripts/extract_frames.py data/videos/gameplay.mp4 data/raw_frames/
   ```

3. **标注数据**
   - 访问 https://cvat.ai
   - 创建项目，上传图片
   - 标注类别：`mature`, `mutated`, `price_tag`
   - 导出为YOLO格式

4. **训练YOLO模型**
   ```bash
   python scripts/train_yolo.py
   ```

## 运行框架

```bash
python main.py
```

## 架构概览

```
手机游戏
   ↓
Device Layer (ADB) ← 
   ↓                 ↑
Capture Layer        |
   ↓                 |
Perception (YOLO+OCR)|
   ↓                 |
World State          |
   ↓                 |
FSM                  |
   ↓                 |
Rule Engine          |
   ↓                 |
Action Layer ────────┘
```

## 常见问题

### Q: adb devices 显示 unauthorized
A: 手机上重新允许USB调试授权

### Q: 截图失败
A: 
1. 检查 `adb shell screencap -p` 是否正常
2. 确认手机屏幕已解锁

### Q: YOLO模型在哪？
A: 需要先准备数据集并训练，或使用预训练模型

### Q: 如何添加自定义规则？
A: 编辑 `src/rules/rule_engine.py`，在 `_setup_rules()` 中添加

## 下一步

1. 准备数据集（参考王者农场方案文档）
2. 训练YOLO模型
3. 调整规则引擎
4. 测试完整流程

## 项目结构

```
mobile-auto-framework/
├── main.py              # 主入口
├── src/                 # 源代码
│   ├── device/          # 设备控制
│   ├── capture/         # 截图/录屏
│   ├── perception/      # AI识别
│   ├── world/           # 状态模型
│   ├── fsm/             # 状态机
│   ├── rules/           # 规则引擎
│   └── action/          # 动作执行
├── tests/               # 测试
├── data/                # 数据
│   ├── models/          # YOLO模型
│   ├── screenshots/     # 截图
│   └── videos/          # 录屏
├── configs/             # 配置
└── docs/                # 文档
```
