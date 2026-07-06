#!/usr/bin/env python3
"""
视频切帧脚本 - 从录屏视频中提取图像帧
用于数据采集阶段，将30分钟游戏录屏转换为1800张候选图片

使用方法:
    python scripts/extract_frames.py <video_path> <output_dir> [--fps 1]

示例:
    python scripts/extract_frames.py data/videos/gameplay.mp4 data/raw_frames/
    python scripts/extract_frames.py data/videos/gameplay.mp4 data/raw_frames/ --fps 0.5
"""

import cv2
import sys
import os
from pathlib import Path
import argparse


def extract_frames(video_path, output_dir, fps_interval=1):
    """
    从视频中提取帧

    Args:
        video_path: 视频文件路径
        output_dir: 输出目录
        fps_interval: 每秒提取几帧 (默认1帧/秒)

    Returns:
        提取的帧数
    """
    # 检查视频文件
    if not os.path.exists(video_path):
        print(f"❌ 视频文件不存在: {video_path}")
        return 0

    # 创建输出目录
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # 打开视频
    video = cv2.VideoCapture(video_path)
    if not video.isOpened():
        print(f"❌ 无法打开视频文件: {video_path}")
        return 0

    # 获取视频信息
    fps = video.get(cv2.CAP_PROP_FPS)
    total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = total_frames / fps if fps > 0 else 0

    print("=" * 60)
    print("视频信息")
    print("=" * 60)
    print(f"文件路径: {video_path}")
    print(f"FPS: {fps:.2f}")
    print(f"总帧数: {total_frames}")
    print(f"时长: {duration:.2f}秒 ({duration/60:.2f}分钟)")
    print(f"提取间隔: {fps_interval} 帧/秒")
    print(f"输出目录: {output_dir}")
    print("=" * 60)
    print()

    # 计算帧间隔
    frame_interval = int(fps / fps_interval) if fps > 0 else 30

    # 提取帧
    count = 0
    saved = 0

    print("开始提取...")

    while True:
        ret, frame = video.read()
        if not ret:
            break

        # 每隔指定帧数保存一张
        if count % frame_interval == 0:
            output_path = output_dir / f"frame_{saved:04d}.jpg"
            cv2.imwrite(str(output_path), frame)
            saved += 1

            # 每保存100张显示一次进度
            if saved % 100 == 0:
                progress = (count / total_frames) * 100 if total_frames > 0 else 0
                print(f"  进度: {progress:.1f}% - 已保存 {saved} 张")

        count += 1

    video.release()

    print()
    print("=" * 60)
    print("✓ 提取完成")
    print("=" * 60)
    print(f"总共提取: {saved} 张图片")
    print(f"平均每秒: {saved/duration:.2f} 张" if duration > 0 else "")
    print(f"保存位置: {output_dir.absolute()}")
    print("=" * 60)
    print()
    print("下一步:")
    print("  1. 人工筛选高质量图片（删除重复、模糊的）")
    print("  2. 使用 Label Studio 标注数据")
    print("  3. 导出为 YOLO 格式")

    return saved


def main():
    parser = argparse.ArgumentParser(
        description='从游戏录屏视频中提取帧用于数据集制作',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 每秒提取1帧（默认）
  python scripts/extract_frames.py data/videos/gameplay.mp4 data/raw_frames/

  # 每秒提取0.5帧（2秒1帧）
  python scripts/extract_frames.py data/videos/gameplay.mp4 data/raw_frames/ --fps 0.5

  # 每秒提取2帧
  python scripts/extract_frames.py data/videos/gameplay.mp4 data/raw_frames/ --fps 2
        """
    )

    parser.add_argument('video_path', help='输入视频文件路径')
    parser.add_argument('output_dir', help='输出图片目录')
    parser.add_argument('--fps', type=float, default=1.0,
                       help='每秒提取帧数 (默认: 1.0)')

    args = parser.parse_args()

    # 执行提取
    extracted = extract_frames(args.video_path, args.output_dir, args.fps)

    # 返回状态码
    sys.exit(0 if extracted > 0 else 1)


if __name__ == '__main__':
    main()
