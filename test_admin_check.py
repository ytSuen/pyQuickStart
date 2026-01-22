"""
测试管理员权限检测
"""
import ctypes
import sys


def is_admin():
    """检查是否以管理员权限运行"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


def main():
    print("=" * 50)
    print("管理员权限检测测试")
    print("=" * 50)
    print()
    
    if is_admin():
        print("✓ 当前以管理员权限运行")
        print()
        print("可以正常使用全局快捷键功能")
    else:
        print("× 当前未以管理员权限运行")
        print()
        print("请右键点击程序，选择'以管理员身份运行'")
        print("否则全局快捷键将无法正常工作")
    
    print()
    print("=" * 50)
    input("按回车键退出...")


if __name__ == "__main__":
    main()
