#!/usr/bin/env python3
"""验证环境安装"""
import subprocess
import sys


def check_import(module_name, import_name=None, display_name=None):
    """检查模块是否可导入"""
    if import_name is None:
        import_name = module_name
    if display_name is None:
        display_name = module_name

    try:
        __import__(import_name)
        print(f"✓ {display_name}")
        return True
    except ImportError:
        print(f"✗ {display_name} - 未安装")
        return False


def check_command(cmd):
    """检查命令是否可用"""
    try:
        result = subprocess.run(
            [cmd, '--version'],
            capture_output=True,
            timeout=5,
            text=True
        )
        if result.returncode == 0:
            print(f"✓ {cmd}")
            return True
        else:
            print(f"✗ {cmd} - 未安装或不可用")
            return False
    except FileNotFoundError:
        print(f"✗ {cmd} - 未安装")
        return False
    except Exception as e:
        print(f"✗ {cmd} - 检查失败: {e}")
        return False


def main():
    print("=" * 50)
    print("环境检查")
    print("=" * 50)

    results = []

    print("\n【Python 包】")
    results.append(check_import("adbutils"))
    results.append(check_import("ultralytics"))
    results.append(check_import("paddleocr"))
    results.append(check_import("transitions"))
    results.append(check_import("label_studio", display_name="label-studio"))
    results.append(check_import("numpy"))
    results.append(check_import("PIL", "pillow", "pillow"))
    results.append(check_import("cv2", "cv2", "opencv-python"))
    results.append(check_import("yaml", "yaml", "pyyaml"))

    print("\n【系统工具】")
    results.append(check_command("adb"))
    results.append(check_command("scrcpy"))

    print("\n" + "=" * 50)
    passed = sum(results)
    total = len(results)

    if passed == total:
        print(f"✓ 环境检查通过: {passed}/{total}")
        print("=" * 50)
        print("\n下一步:")
        print("  python tests/test_device.py  # 测试设备连接")
        return 0
    else:
        print(f"✗ 环境检查失败: {passed}/{total}")
        print("=" * 50)
        print("\n请运行安装脚本:")
        print("  macOS:   ./setup_mac.sh")
        print("  Windows: setup_windows.bat")
        return 1


if __name__ == '__main__':
    sys.exit(main())
