"""
Capture Layer - 截图/录屏层
负责从设备捕获画面数据
"""
import subprocess
import time
from pathlib import Path
from typing import Optional
import numpy as np
from PIL import Image
import io


class ScreenCapture:
    """屏幕捕获器 - 负责截图和录屏"""

    def __init__(self, device_id: Optional[str] = None, output_dir: str = "data/screenshots"):
        """
        初始化捕获器
        :param device_id: 设备ID
        :param output_dir: 输出目录
        """
        self.device_id = device_id
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def screenshot(self, save_path: Optional[str] = None) -> Optional[np.ndarray]:
        """
        截取屏幕
        :param save_path: 保存路径（可选）
        :return: numpy数组格式的图像 (H, W, 3) BGR格式，失败返回None
        """
        try:
            cmd = ['adb']
            if self.device_id:
                cmd.extend(['-s', self.device_id])
            cmd.extend(['exec-out', 'screencap', '-p'])

            # 执行截图命令
            result = subprocess.run(cmd, capture_output=True, timeout=5)
            if result.returncode != 0:
                print(f"[Capture] Screenshot failed: {result.stderr}")
                return None

            # 将字节流转为PIL图像
            image = Image.open(io.BytesIO(result.stdout))

            # 转为numpy数组 (RGB -> BGR for OpenCV)
            img_array = np.array(image)
            img_bgr = img_array[:, :, ::-1].copy()  # RGB to BGR

            # 保存到文件（可选）
            if save_path:
                save_path = Path(save_path)
                save_path.parent.mkdir(parents=True, exist_ok=True)
                image.save(save_path)
                print(f"[Capture] Saved screenshot to {save_path}")

            return img_bgr

        except Exception as e:
            print(f"[Capture] Screenshot error: {e}")
            return None

    def screenshot_fast(self) -> Optional[np.ndarray]:
        """
        快速截图（用于实时循环，不保存文件）
        :return: numpy数组格式的图像
        """
        return self.screenshot(save_path=None)

    def screenshot_with_timestamp(self) -> Optional[np.ndarray]:
        """
        带时间戳的截图（自动保存）
        :return: numpy数组格式的图像
        """
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        save_path = self.output_dir / f"screenshot_{timestamp}.png"
        return self.screenshot(save_path=str(save_path))

    def start_recording(self, output_path: Optional[str] = None,
                       bitrate: int = 8000000, time_limit: int = 180) -> bool:
        """
        开始录屏（后台进程）
        :param output_path: 输出路径
        :param bitrate: 比特率
        :param time_limit: 时长限制（秒）
        :return: 是否成功启动
        """
        try:
            if output_path is None:
                timestamp = time.strftime("%Y%m%d_%H%M%S")
                output_path = self.output_dir.parent / "videos" / f"record_{timestamp}.mp4"

            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            # 设备端录制路径
            device_path = f"/sdcard/screenrecord_{int(time.time())}.mp4"

            cmd = ['adb']
            if self.device_id:
                cmd.extend(['-s', self.device_id])
            cmd.extend(['shell', 'screenrecord',
                       '--bit-rate', str(bitrate),
                       '--time-limit', str(time_limit),
                       device_path])

            # 后台启动录制
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            print(f"[Capture] Recording started (device path: {device_path})")
            print(f"[Capture] Will save to: {output_path}")

            # 保存进程信息以便后续停止
            self.recording_process = process
            self.recording_device_path = device_path
            self.recording_output_path = output_path

            return True

        except Exception as e:
            print(f"[Capture] Recording start failed: {e}")
            return False

    def stop_recording(self) -> bool:
        """
        停止录屏并拉取到PC
        :return: 是否成功
        """
        try:
            if not hasattr(self, 'recording_process'):
                print("[Capture] No recording in progress")
                return False

            # 发送中断信号
            self.recording_process.terminate()
            self.recording_process.wait(timeout=5)

            # 等待文件写入完成
            time.sleep(2)

            # 从设备拉取录制文件
            cmd = ['adb']
            if self.device_id:
                cmd.extend(['-s', self.device_id])
            cmd.extend(['pull', self.recording_device_path, str(self.recording_output_path)])

            result = subprocess.run(cmd, capture_output=True, timeout=30)

            if result.returncode == 0:
                print(f"[Capture] Recording saved to {self.recording_output_path}")

                # 清理设备端文件
                self._cleanup_device_file(self.recording_device_path)

                return True
            else:
                print(f"[Capture] Failed to pull recording: {result.stderr}")
                return False

        except Exception as e:
            print(f"[Capture] Stop recording error: {e}")
            return False

    def _cleanup_device_file(self, device_path: str):
        """清理设备端文件"""
        try:
            cmd = ['adb']
            if self.device_id:
                cmd.extend(['-s', self.device_id])
            cmd.extend(['shell', 'rm', device_path])
            subprocess.run(cmd, timeout=5)
        except Exception as e:
            print(f"[Capture] Cleanup warning: {e}")


if __name__ == '__main__':
    # 测试截图
    capture = ScreenCapture()
    img = capture.screenshot_with_timestamp()
    if img is not None:
        print(f"Screenshot shape: {img.shape}")
