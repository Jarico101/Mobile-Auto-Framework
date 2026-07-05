"""
测试设备连接和基础功能
"""
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.device.device_controller import DeviceController
from src.capture.screen_capture import ScreenCapture


def test_device_connection():
    """测试设备连接"""
    print("=" * 50)
    print("测试1: 设备连接")
    print("=" * 50)

    device = DeviceController()

    # 列出设备
    devices = device.list_devices()
    print(f"发现 {len(devices)} 台设备: {devices}")

    if not devices:
        print("❌ 没有发现设备，请检查：")
        print("  1. 手机是否连接到电脑")
        print("  2. USB调试是否开启")
        print("  3. ADB是否安装: adb version")
        return False

    # 连接设备
    if device.connect():
        print("✓ 设备连接成功")

        # 获取屏幕尺寸
        size = device.get_screen_size()
        if size:
            print(f"✓ 屏幕尺寸: {size[0]} x {size[1]}")
        else:
            print("⚠ 无法获取屏幕尺寸")

        device.disconnect()
        return True
    else:
        print("❌ 设备连接失败")
        return False


def test_screenshot():
    """测试截图功能"""
    print("\n" + "=" * 50)
    print("测试2: 截图功能")
    print("=" * 50)

    device = DeviceController()
    if not device.connect():
        print("❌ 设备未连接")
        return False

    capture = ScreenCapture(device_id=device.device_id)

    print("正在截图...")
    img = capture.screenshot_with_timestamp()

    if img is not None:
        print(f"✓ 截图成功")
        print(f"  图像尺寸: {img.shape}")
        print(f"  保存路径: {capture.output_dir}")
        device.disconnect()
        return True
    else:
        print("❌ 截图失败")
        device.disconnect()
        return False


def test_tap():
    """测试点击功能（需要手动确认）"""
    print("\n" + "=" * 50)
    print("测试3: 点击功能")
    print("=" * 50)

    device = DeviceController()
    if not device.connect():
        print("❌ 设备未连接")
        return False

    size = device.get_screen_size()
    if not size:
        print("❌ 无法获取屏幕尺寸")
        device.disconnect()
        return False

    # 点击屏幕中心
    x, y = size[0] // 2, size[1] // 2

    print(f"即将点击屏幕中心: ({x}, {y})")
    print("请观察手机屏幕，按回车继续...")
    input()

    if device.tap(x, y):
        print("✓ 点击命令发送成功")
        print("请在手机上确认是否有点击效果")
        device.disconnect()
        return True
    else:
        print("❌ 点击失败")
        device.disconnect()
        return False


def main():
    """运行所有测试"""
    print("""
╔════════════════════════════════════════════════╗
║   设备连接测试                                  ║
╚════════════════════════════════════════════════╝
    """)

    # 运行测试
    results = []

    results.append(("设备连接", test_device_connection()))

    if results[0][1]:  # 如果设备连接成功
        results.append(("截图功能", test_screenshot()))

        print("\n是否测试点击功能？(y/n): ", end="")
        if input().lower() == 'y':
            results.append(("点击功能", test_tap()))

    # 汇总结果
    print("\n" + "=" * 50)
    print("测试结果汇总:")
    print("=" * 50)
    for name, result in results:
        status = "✓ 通过" if result else "❌ 失败"
        print(f"  {name}: {status}")

    passed = sum(1 for _, r in results if r)
    total = len(results)
    print(f"\n总计: {passed}/{total} 通过")


if __name__ == '__main__':
    main()
