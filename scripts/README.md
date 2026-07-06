# Scripts 工具脚本

## extract_frames.py - 视频切帧工具

从游戏录屏视频中提取图像帧，用于制作YOLO训练数据集。

### 使用方法

```bash
python scripts/extract_frames.py <video_path> <output_dir> [--fps 1]
```

### 参数说明

- `video_path`: 输入视频文件路径
- `output_dir`: 输出图片目录
- `--fps`: 每秒提取帧数（可选，默认1.0）

### 示例

```bash
# 每秒提取1帧（30分钟视频 → 1800张图）
python scripts/extract_frames.py data/videos/gameplay.mp4 data/raw_frames/

# 每2秒提取1帧（30分钟视频 → 900张图）
python scripts/extract_frames.py data/videos/gameplay.mp4 data/raw_frames/ --fps 0.5

# 每秒提取2帧（30分钟视频 → 3600张图）
python scripts/extract_frames.py data/videos/gameplay.mp4 data/raw_frames/ --fps 2
```

### 工作流程

1. **录制视频** - 游玩30分钟，录制游戏画面
   ```bash
   # 方式1: 手机自带录屏
   # 方式2: ADB录屏
   adb shell screenrecord --time-limit 180 /sdcard/gameplay.mp4
   adb pull /sdcard/gameplay.mp4 data/videos/
   
   # 方式3: scrcpy录屏
   scrcpy --record data/videos/gameplay.mp4
   ```

2. **提取帧** - 使用本脚本
   ```bash
   python scripts/extract_frames.py data/videos/gameplay.mp4 data/raw_frames/
   ```

3. **筛选图片** - 人工删除重复、模糊、无用的图片
   - 目标：1800张 → 500张高质量图片

4. **标注数据** - 使用 Label Studio
   ```bash
   label-studio
   # 浏览器访问 http://localhost:8080
   # 标注类别: mature, mutated, price_tag
   ```

5. **导出数据集** - 导出为 YOLO 格式
   - 放入 `data/images/` 和 `data/labels/`

### 输出示例

```
==================================================
视频信息
==================================================
文件路径: data/videos/gameplay.mp4
FPS: 30.00
总帧数: 54000
时长: 1800.00秒 (30.00分钟)
提取间隔: 1.0 帧/秒
输出目录: data/raw_frames
==================================================

开始提取...
  进度: 16.7% - 已保存 100 张
  进度: 33.3% - 已保存 200 张
  ...

==================================================
✓ 提取完成
==================================================
总共提取: 1800 张图片
平均每秒: 1.00 张
保存位置: /path/to/data/raw_frames
==================================================
```

### 注意事项

- 确保已安装 `opencv-python`: `pip install opencv-python`
- 建议30分钟视频使用 `--fps 1`（提取1800张）
- 提取后需要人工筛选，删除质量差的图片
- 最终目标：500张高质量、场景多样的训练图片
