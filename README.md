# Mobile Automation Framework

基于感知-决策-执行闭环的手机游戏自动化框架

## 快速开始

### 1. 克隆项目

```bash
git clone <your-repo-url>
cd mobile-auto-framework
```

### 2. 安装依赖

**macOS:**
```bash
./setup_mac.sh
```

**Windows:**
```bash
setup_windows.bat
```

### 3. 验证环境

```bash
python verify_env.py
```

### 4. 测试设备连接

```bash
python tests/test_device.py
```

### 5. 运行框架

```bash
python main.py
```

---

## 架构设计

```
┌─────────────┐   ┌──────────┐   ┌─────────────────────┐
│  手机游戏    │ → │ Device   │ → │ Capture(截图)        │
└─────────────┘   │ (ADB)    │   └─────────────────────┘
                  └──────────┘              ↓
                                   ┌─────────────────────┐
                                   │ Perception          │
                                   │ (YOLO + OCR)        │
                                   └─────────────────────┘
                                            ↓
                                   ┌─────────────────────┐
                                   │ World State         │
                                   └─────────────────────┘
                                            ↓
                                   ┌─────────────────────┐
                                   │ FSM                 │
                                   └─────────────────────┘
                                            ↓
                                   ┌─────────────────────┐
                                   │ Rule Engine         │
                                   └─────────────────────┘
                                            ↓
                                   ┌─────────────────────┐
                                   │ Action (贝塞尔)      │
                                   └─────────────────────┘
                                            ↓
                                   ┌─────────────────────┐
                                   │ ADB 执行             │
                                   └─────────────────────┘
                                            ↓
                                          循环
```

**数据流：** 游戏画面 → 感知 → 状态 → 决策 → 动作 → 执行 → 循环

---

## 目录结构

```
mobile-auto-framework/
├── src/
│   ├── device/          # 设备层：ADB/scrcpy连接
│   ├── capture/         # 捕获层：截图/录屏
│   ├── perception/      # 感知层：YOLO/OCR
│   ├── world/           # 世界状态模型
│   ├── fsm/             # 有限状态机
│   ├── rules/           # 规则引擎
│   └── action/          # 动作执行层
├── tests/               # 单元测试
├── data/
│   ├── models/          # YOLO模型权重
│   ├── screenshots/     # 截图数据
│   └── videos/          # 录屏数据
├── configs/             # 配置文件
├── logs/                # 运行日志
└── docs/                # 文档
```

---

## 技术栈

- **设备控制**: adbutils
- **目标检测**: YOLOv8
- **文字识别**: PaddleOCR
- **状态机**: transitions
- **拟人化**: 贝塞尔曲线 + 高斯分布

---

## 文档

- [CLAUDE.md](CLAUDE.md) - Agent 协作指南
- [docs/SETUP.md](docs/SETUP.md) - 环境安装详细说明
- [docs/QUICKSTART.md](docs/QUICKSTART.md) - 快速上手教程

---

## 开发计划

- [x] 项目立项与架构设计
- [x] 完整代码框架
- [x] 安装脚本与文档
- [ ] 数据采集与标注
- [ ] YOLO 模型训练
- [ ] 集成测试
- [ ] 性能优化

---

## License

MIT
