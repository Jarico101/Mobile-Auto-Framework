"""
Device Layer - 设备连接与控制层
负责与Android设备的通信（ADB/scrcpy）
"""
import subprocess
import time
from typing import Optional, List, Tuple


class DeviceController:
    """设备控制器 - 负责ADB连接和基础命令执行"""

    def __init__(self, device_id: Optional[str] = None):
        """
        初始化设备控制器
        :param device_id: 设备ID，None则使用第一个连接的设备
        """
        self.device_id = device_id
        self.connected = False

    def connect(self) -> bool:
        """
        连接设备
        :return: 连接是否成功
        """
        try:
            # 检查ADB是否可用
            result = subprocess.run(['adb', 'version'],
                                  capture_output=True, text=True, timeout=5)
            if result.returncode != 0:
                print("[Device] ADB not found")
                return False

            # 获取设备列表
            devices = self.list_devices()
            if not devices:
                print("[Device] No devices connected")
                return False

            # 选择设备
            if self.device_id is None:
                self.device_id = devices[0]
                print(f"[Device] Auto-selected device: {self.device_id}")
            elif self.device_id not in devices:
                print(f"[Device] Device {self.device_id} not found")
                return False

            self.connected = True
            print(f"[Device] Connected to {self.device_id}")
            return True

        except Exception as e:
            print(f"[Device] Connection failed: {e}")
            return False

    def list_devices(self) -> List[str]:
        """
        列出所有连接的设备
        :return: 设备ID列表
        """
        try:
            result = subprocess.run(['adb', 'devices'],
                                  capture_output=True, text=True, timeout=5)
            lines = result.stdout.strip().split('\n')[1:]  # 跳过第一行标题
            devices = []
            for line in lines:
                if '\tdevice' in line:
                    device_id = line.split('\t')[0]
                    devices.append(device_id)
            return devices
        except Exception as e:
            print(f"[Device] Failed to list devices: {e}")
            return []

    def get_screen_size(self) -> Optional[Tuple[int, int]]:
        """
        获取屏幕分辨率
        :return: (width, height) 或 None
        """
        if not self.connected:
            return None

        try:
            cmd = ['adb']
            if self.device_id:
                cmd.extend(['-s', self.device_id])
            cmd.extend(['shell', 'wm', 'size'])

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
            # 输出格式: "Physical size: 1080x1920"
            output = result.stdout.strip()
            if 'Physical size:' in output:
                size_str = output.split(':')[1].strip()
                w, h = map(int, size_str.split('x'))
                return (w, h)
            return None
        except Exception as e:
            print(f"[Device] Failed to get screen size: {e}")
            return None

    def shell(self, command: str, timeout: int = 10) -> Optional[str]:
        """
        执行shell命令
        :param command: shell命令
        :param timeout: 超时时间（秒）
        :return: 命令输出或None
        """
        if not self.connected:
            print("[Device] Device not connected")
            return None

        try:
            cmd = ['adb']
            if self.device_id:
                cmd.extend(['-s', self.device_id])
            cmd.extend(['shell', command])

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
            return result.stdout.strip()
        except Exception as e:
            print(f"[Device] Shell command failed: {e}")
            return None

    def tap(self, x: int, y: int) -> bool:
        """
        点击屏幕坐标
        :param x: X坐标
        :param y: Y坐标
        :return: 是否成功
        """
        result = self.shell(f'input tap {x} {y}')
        return result is not None

    def swipe(self, x1: int, y1: int, x2: int, y2: int, duration: int = 300) -> bool:
        """
        滑动屏幕
        :param x1: 起点X
        :param y1: 起点Y
        :param x2: 终点X
        :param y2: 终点Y
        :param duration: 滑动时长（毫秒）
        :return: 是否成功
        """
        result = self.shell(f'input swipe {x1} {y1} {x2} {y2} {duration}')
        return result is not None

    def disconnect(self):
        """断开连接"""
        self.connected = False
        print(f"[Device] Disconnected")


if __name__ == '__main__':
    # 测试设备连接
    device = DeviceController()
    if device.connect():
        print(f"Screen size: {device.get_screen_size()}")
        device.disconnect()
