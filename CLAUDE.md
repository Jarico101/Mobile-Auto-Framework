# Mobile Automation Framework - Agent 协作指南

## 项目概述

这是一个基于感知-决策-执行闭环的手机游戏自动化框架，采用多Agent分工协作模式开发。

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
                                   │ Action              │
                                   └─────────────────────┘
                                            ↓
                                   ┌─────────────────────┐
                                   │ ADB 执行             │
                                   └─────────────────────┘
                                            ↓
                                          循环
```

**数据流：** 游戏画面 → 感知 → 状态 → 决策 → 动作 → 执行 → 循环

## 开发协作

- **Claude**：架构设计、代码审查、验收
- **Codex**：功能开发、调试、测试
- **Coworker**：任务拆分、并行执行（如使用）

---

## 模块分工

### Module 1: Device & Capture
**负责模块：**
- `src/device/device_controller.py` - 设备连接与ADB控制
- `src/capture/screen_capture.py` - 截图与录屏

**职责：**
- 维护设备连接稳定性
- 优化截图性能（延迟<100ms）
- 实现录屏功能
- 处理设备异常（掉线、超时）

**依赖：** 无（最底层）

---

### Module 2: Perception
**负责模块：**
- `src/perception/perception_engine.py` - YOLO + OCR 感知引擎

**职责：**
- 集成YOLOv8目标检测
- 集成PaddleOCR文字识别
- 优化推理速度（<30ms）
- 提供统一的感知接口

**依赖：**
- 需要 Module 1 提供的截图数据

**输入：** `np.ndarray` (图像)  
**输出：** `List[Detection]` (检测结果)

---

### Module 3: World & FSM
**负责模块：**
- `src/world/world_model.py` - 世界状态模型
- `src/fsm/game_fsm.py` - 有限状态机

**职责：**
- 维护游戏世界状态
- 管理游戏对象（作物、价格标签等）
- 实现页面/状态识别逻辑
- 状态转换管理

**依赖：**
- 需要 Module 2 提供的感知结果

**输入：** `perception_result` (感知结果)  
**输出：** `WorldState`, `GameState` (当前状态)

---

### Module 4: Rule & Decision
**负责模块：**
- `src/rules/rule_engine.py` - 规则引擎与决策系统

**职责：**
- 设计游戏规则
- 实现决策逻辑
- 优先级管理
- 策略切换

**依赖：**
- 需要 Module 3 提供的世界状态和FSM状态

**输入：** `context = {world, fsm, image}`  
**输出：** `Decision(action, params, reason)`

---

### Module 5: Action
**负责模块：**
- `src/action/action_executor.py` - 动作执行与拟人化

**职责：**
- 实现贝塞尔曲线轨迹
- 高斯分布随机延迟
- 拟人化点击/滑动
- 复合动作（收获、翻页等）

**依赖：**
- 需要 Module 1 的设备控制器
- 需要 Module 4 的决策结果

**输入：** `Decision` (决策)  
**输出：** 执行动作

---

### Module 6: Integration
**负责模块：**
- `main.py` - 主控制循环
- `configs/config.yaml` - 配置管理
- `tests/` - 集成测试

**职责：**
- 整合所有模块
- 实现主循环
- 异常处理
- 性能监控
- 编写测试用例

**依赖：** 所有其他模块

---

## 开发规范

### 1. 模块独立性
- 每个模块必须**独立可测试**
- 通过明确的接口（输入/输出）通信
- 不允许跨层直接调用

### 2. 接口契约
所有模块必须遵守以下接口规范：

```python
# 示例：Perception Layer
class PerceptionEngine:
    def perceive(self, image: np.ndarray) -> Dict:
        """
        输入：BGR图像 (H, W, 3)
        输出：{'detections': List[Detection], ...}
        """
        pass
```

### 3. 错误处理
- 所有模块必须优雅处理异常
- 返回 `None` 或空结果而不是抛出异常
- 记录错误日志

### 4. 测试要求
每个模块需提供：
- 单元测试（`tests/test_<module>.py`）
- 独立运行的 `if __name__ == '__main__'` 测试

### 5. 代码风格
- 使用类型注解（Type Hints）
- 函数必须有docstring
- 变量命名清晰（避免单字母）

---

## 开发流程

### Phase 1: 独立开发
- 每个模块独立开发
- 使用mock数据进行单元测试
- 完成后提交PR

### Phase 2: 接口联调
- Module 1 + Module 2：设备 → 感知
- Module 2 + Module 3：感知 → 状态
- Module 3 + Module 4：状态 → 决策
- Module 4 + Module 5：决策 → 执行

### Phase 3: 系统集成
- Module 6 整合所有模块
- 端到端测试
- 性能优化

### 沟通协议

**接口变更：**
- 必须在 `CHANGELOG.md` 中记录
- 通知下游依赖的模块

**Bug报告：**
- 使用 `# TODO: <Module X> - <问题描述>` 标记
- 在对应模块文件中添加注释

**代码审查：**
- 每个模块的修改需要相邻层review
- 例如：Module 2 的代码需要 Module 1 和 Module 3 review

---

## 当前状态

### ✅ 已完成
- 项目框架搭建
- 所有模块骨架代码
- 设备连接测试
- 主循环逻辑

### 🚧 待完成（按优先级）

**P0 - 核心功能：**
- [ ] Module 2: 集成真实的YOLO模型
- [ ] Module 2: 集成PaddleOCR
- [ ] Module 3: 完善状态识别逻辑
- [ ] Module 5: 测试贝塞尔曲线轨迹

**P1 - 数据准备：**
- [ ] 录屏采集游戏素材
- [ ] 标注数据集（CVAT）
- [ ] 训练YOLO模型

**P2 - 优化：**
- [ ] 性能优化（推理速度）
- [ ] 拟人化参数调优
- [ ] 异常恢复机制

---

## 快速开始

### 环境搭建
```bash
cd /Users/x/Documents/mobile-auto-framework
pip install -r requirements.txt
```

### 测试设备连接
```bash
python tests/test_device.py
```

### 开发单个模块
```bash
# 例如：开发感知层
python src/perception/perception_engine.py
```

### 运行完整系统
```bash
python main.py
```

---

## 关键文件位置

- **项目根目录：** `/Users/x/Documents/mobile-auto-framework/`
- **配置文件：** `configs/config.yaml`
- **YOLO模型：** `data/models/best.pt`（需训练）
- **测试数据：** `data/screenshots/`
- **日志：** `logs/`

---

## 注意事项

1. **模块职责明确** - 每个模块只负责自己的功能
2. **保持接口稳定** - 接口变更必须向后兼容或通知所有相关方
3. **测试先行** - 提交代码前必须通过单元测试
4. **文档同步** - 代码变更后更新对应文档

---

## 参考文档

- 架构设计：本文档
- 快速开始：`docs/QUICKSTART.md`
- 项目说明：`README.md`
- 王者农场方案：`/Users/x/Downloads/王者农场AI项目方案.md`
